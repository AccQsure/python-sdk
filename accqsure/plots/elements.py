from __future__ import annotations
from dataclasses import dataclass, field, fields
from typing import Optional, Any, TYPE_CHECKING, List, Tuple

if TYPE_CHECKING:
    from accqsure import AccQsure


class PlotElements(object):
    """Manager for plot element resources.

    Provides methods to retrieve and list plot elements.
    Elements are the content units within plot sections. Maps to the
    /v1/plot/{plot_id}/section/{section_id}/element API endpoints.
    """

    def __init__(
        self,
        accqsure: "AccQsure",
        plot_id: str,
        plot_section_id: str,
    ) -> None:
        """Initialize the PlotElements manager.

        Args:
            accqsure: The AccQsure client instance.
            plot_id: The plot ID this manager is associated with.
            plot_section_id: The section ID this manager is associated with.
        """
        self.accqsure = accqsure
        self.plot_id = plot_id
        self.section_id = plot_section_id

    async def get(self, id_: str, **kwargs: Any) -> Optional["PlotElement"]:
        """Get a plot element by ID.

        Retrieves a single plot element by its entity ID.

        Args:
            id_: Plot element entity ID (24-character string).
            **kwargs: Additional query parameters.

        Returns:
            PlotElement instance if found, None otherwise.

        Raises:
            ApiError: If the API returns an error.
            AccQsureException: If there's an error making the request.
        """
        resp = await self.accqsure._query(
            f"/plot/{self.plot_id}/section/{self.section_id}/element/{id_}",
            "GET",
            kwargs,
        )
        return PlotElement.from_api(
            self.accqsure, self.plot_id, self.section_id, resp
        )

    async def list(
        self,
        limit: int = 50,
        start_key: Optional[str] = None,
        **kwargs: Any,
    ) -> Tuple[List["PlotElement"], Optional[str]]:
        """List plot elements.

        Retrieves a paginated list of elements for this plot section.

        Args:
            limit: Number of results to return (default: 50, max: 100).
            start_key: Pagination cursor from previous response.
            **kwargs: Additional query parameters.

        Returns:
            Tuple of (list of PlotElement instances, last_key for pagination).

        Raises:
            ApiError: If the API returns an error.
            AccQsureException: If there's an error making the request.
        """
        resp = await self.accqsure._query(
            f"/plot/{self.plot_id}/section/{self.section_id}/element",
            "GET",
            {"limit": limit, "start_key": start_key, **kwargs},
        )
        plot_elements = [
            PlotElement.from_api(
                self.accqsure, self.plot_id, self.section_id, plot_element
            )
            for plot_element in resp.get("results")
        ]
        return plot_elements, resp.get("last_key")


@dataclass
class PlotElement:
    """Represents an element within a plot section.

    Elements are the content units within plot sections. They contain
    generated content and have a status indicating their generation state.

    Attributes:
        plot_id: The plot ID this element belongs to.
        section_id: The section ID this element belongs to.
        id: Entity ID of the element.
        order: Display order of the element.
        type: Element type (should be one of CHART_ELEMENT_TYPE enum values:
              'title', 'narrative', 'table', or 'static').
        status: Generation status of the element.
        created_at: Creation timestamp.
        updated_at: Last update timestamp.
        content: Generated content of the element.
    """

    plot_id: str
    section_id: str
    id: str
    order: int
    type: str  # Should be one of CHART_ELEMENT_TYPE enum values
    status: str
    created_at: Optional[str] = field(default=None)
    updated_at: Optional[str] = field(default=None)
    content: Optional[str] = field(default=None)

    @classmethod
    def from_api(
        cls,
        accqsure: "AccQsure",
        plot_id: str,
        section_id: str,
        data: dict[str, Any],
    ) -> Optional["PlotElement"]:
        """Create a PlotElement instance from API response data.

        Args:
            accqsure: The AccQsure client instance.
            plot_id: The plot ID this element belongs to.
            section_id: The section ID this element belongs to.
            data: Dictionary containing plot element data from the API.

        Returns:
            PlotElement instance if data is provided, None otherwise.
        """
        if not data:
            return None
        entity = cls(
            plot_id=plot_id,
            section_id=section_id,
            id=data.get("entity_id"),
            order=data.get("order"),
            type=data.get("type"),
            status=data.get("status"),
            content=data.get("content"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
        )
        entity.accqsure = accqsure
        return entity

    @property
    def accqsure(self) -> "AccQsure":
        """Get the AccQsure client instance."""
        return self._accqsure

    @accqsure.setter
    def accqsure(self, value: "AccQsure") -> None:
        """Set the AccQsure client instance."""
        self._accqsure = value

    async def refresh(self) -> "PlotElement":
        """Refresh the plot element data from the API.

        Fetches the latest plot element data from the API and updates the
        instance fields.

        Returns:
            Self for method chaining.

        Raises:
            ApiError: If the API returns an error.
            AccQsureException: If there's an error making the request.
        """
        resp = await self.accqsure._query(
            f"/plot/{self.plot_id}/section/{self.section_id}/element/{self.id}",
            "GET",
        )
        exclude = ["id", "plot_id", "section_id", "accqsure"]

        for f in fields(self.__class__):
            if (
                f.name not in exclude
                and f.init
                and resp.get(f.name) is not None
            ):  # Only update init args
                setattr(self, f.name, resp.get(f.name))
        return self
