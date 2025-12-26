from __future__ import annotations
from dataclasses import dataclass, field, fields
from typing import Optional, Any, TYPE_CHECKING, List, Tuple

from .elements import PlotElements

if TYPE_CHECKING:
    from accqsure import AccQsure


class PlotSections(object):
    """Manager for plot section resources.

    Provides methods to retrieve and list plot sections.
    Sections organize plot content hierarchically. Maps to the
    /v1/plot/{plot_id}/section API endpoints.
    """

    def __init__(self, accqsure: "AccQsure", plot_id: str) -> None:
        """Initialize the PlotSections manager.

        Args:
            accqsure: The AccQsure client instance.
            plot_id: The plot ID this manager is associated with.
        """
        self.accqsure = accqsure
        self.plot_id = plot_id

    async def get(self, id_: str, **kwargs: Any) -> Optional["PlotSection"]:
        """Get a plot section by ID.

        Retrieves a single plot section by its entity ID.

        Args:
            id_: Plot section entity ID (24-character string).
            **kwargs: Additional query parameters.

        Returns:
            PlotSection instance if found, None otherwise.

        Raises:
            ApiError: If the API returns an error.
            AccQsureException: If there's an error making the request.
        """
        resp = await self.accqsure._query(
            f"/plot/{self.plot_id}/section/{id_}", "GET", kwargs
        )
        return PlotSection.from_api(self.accqsure, self.plot_id, resp)

    async def list(
        self,
        limit: int = 50,
        start_key: Optional[str] = None,
        **kwargs: Any,
    ) -> Tuple[List["PlotSection"], Optional[str]]:
        """List plot sections.

        Retrieves a paginated list of sections for this plot.

        Args:
            limit: Number of results to return (default: 50, max: 100).
            start_key: Pagination cursor from previous response.
            **kwargs: Additional query parameters.

        Returns:
            Tuple of (list of PlotSection instances, last_key for pagination).

        Raises:
            ApiError: If the API returns an error.
            AccQsureException: If there's an error making the request.
        """
        resp = await self.accqsure._query(
            f"/plot/{self.plot_id}/section",
            "GET",
            {"limit": limit, "start_key": start_key, **kwargs},
        )
        plot_sections = [
            PlotSection.from_api(self.accqsure, self.plot_id, plot_section)
            for plot_section in resp.get("results")
        ]
        return plot_sections, resp.get("last_key")


@dataclass
class PlotSection:
    """Represents a section within a plot.

    Sections organize plot content hierarchically. Each section has
    a heading, style, order, and can contain elements.

    Attributes:
        plot_id: The plot ID this section belongs to.
        id: Entity ID of the section.
        heading: Section heading text.
        style: Section style (should be one of CHART_SECTION_STYLE enum values:
               'title', 'h1', 'h2', 'h3', 'h4', 'h5', or 'h6').
        order: Display order of the section.
        created_at: Creation timestamp.
        updated_at: Last update timestamp.
        number: Optional section number.
    """

    plot_id: str
    id: str
    heading: str
    style: str  # Should be one of CHART_SECTION_STYLE enum values
    order: int
    created_at: Optional[str] = field(default=None)
    updated_at: Optional[str] = field(default=None)
    number: Optional[str] = field(default=None)

    elements: PlotElements = field(
        init=False, repr=False, compare=False, hash=False
    )

    @classmethod
    def from_api(
        cls, accqsure: "AccQsure", plot_id: str, data: dict[str, Any]
    ) -> Optional["PlotSection"]:
        """Create a PlotSection instance from API response data.

        Args:
            accqsure: The AccQsure client instance.
            plot_id: The plot ID this section belongs to.
            data: Dictionary containing plot section data from the API.

        Returns:
            PlotSection instance if data is provided, None otherwise.
        """
        if not data:
            return None
        entity = cls(
            plot_id=plot_id,
            id=data.get("entity_id"),
            heading=data.get("heading"),
            number=data.get("number"),
            style=data.get("style"),
            order=data.get("order"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
        )
        entity.accqsure = accqsure
        entity.elements = PlotElements(
            entity.accqsure, entity.plot_id, entity.id
        )
        return entity

    @property
    def accqsure(self) -> "AccQsure":
        """Get the AccQsure client instance."""
        return self._accqsure

    @accqsure.setter
    def accqsure(self, value: "AccQsure") -> None:
        """Set the AccQsure client instance."""
        self._accqsure = value

    async def refresh(self) -> "PlotSection":
        """Refresh the plot section data from the API.

        Fetches the latest plot section data from the API and updates the
        instance fields.

        Returns:
            Self for method chaining.

        Raises:
            ApiError: If the API returns an error.
            AccQsureException: If there's an error making the request.
        """
        resp = await self.accqsure._query(
            f"/plot/{self.plot_id}/section/{self.id}",
            "GET",
        )
        exclude = ["id", "plot_id", "accqsure"]

        for f in fields(self.__class__):
            if (
                f.name not in exclude
                and f.init
                and resp.get(f.name) is not None
            ):  # Only update init args (skip derived like elements)
                setattr(self, f.name, resp.get(f.name))
        return self
