from __future__ import annotations
from dataclasses import dataclass, field, fields
import logging
from typing import Optional, Any, List, Dict, TYPE_CHECKING, Tuple
from accqsure.charts.waypoints import ChartWaypoint

from accqsure.enums import CHART_ELEMENT_TYPE

if TYPE_CHECKING:
    from accqsure import AccQsure


class ChartElements:
    """Manager for chart element resources.

    Provides methods to create, retrieve, list, and delete chart elements.
    Elements are the content units within chart sections.
    """

    def __init__(
        self,
        accqsure: "AccQsure",
        chart_id: str,
        chart_section_id: str,
    ) -> None:
        """Initialize the ChartElements manager.

        Args:
            accqsure: The AccQsure client instance.
            chart_id: The chart ID this manager is associated with.
            chart_section_id: The section ID this manager is associated with.
        """
        self.accqsure = accqsure
        self.chart_id = chart_id
        self.section_id = chart_section_id

    async def get(self, id_: str, **kwargs: Any) -> Optional["ChartElement"]:
        """Get a chart element by ID.

        Retrieves a single chart element by its entity ID.

        Args:
            id_: Chart element entity ID (24-character string).
            **kwargs: Additional query parameters.

        Returns:
            ChartElement instance if found, None otherwise.

        Raises:
            ApiError: If the API returns an error.
            AccQsureException: If there's an error making the request.
        """
        resp = await self.accqsure._query(
            f"/chart/{self.chart_id}/section/{self.section_id}/element/{id_}",
            "GET",
            kwargs,
        )
        return ChartElement.from_api(
            self.accqsure, self.chart_id, self.section_id, resp
        )

    async def list(
        self,
        limit: int = 50,
        start_key: Optional[str] = None,
        **kwargs: Any,
    ) -> Tuple[List["ChartElement"], Optional[str]]:
        """List chart elements.

        Retrieves a paginated list of elements for this chart section.

        Args:
            limit: Number of results to return (default: 50, max: 100).
            start_key: Pagination cursor from previous response.
            **kwargs: Additional query parameters.

        Returns:
            Tuple of (list of ChartElement instances, last_key for pagination).

        Raises:
            ApiError: If the API returns an error.
            AccQsureException: If there's an error making the request.
        """
        resp = await self.accqsure._query(
            f"/chart/{self.chart_id}/section/{self.section_id}/element",
            "GET",
            {"limit": limit, "start_key": start_key, **kwargs},
        )
        chart_elements = [
            ChartElement.from_api(
                self.accqsure, self.chart_id, self.section_id, chart_element
            )
            for chart_element in resp.get("results")
        ]
        return chart_elements, resp.get("last_key")

    async def create(
        self,
        order: int,
        element_type: CHART_ELEMENT_TYPE,
        description: str,
        prompt: str,
        for_each: bool,
        waypoints: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> "ChartElement":
        """Create a new chart element.

        Creates a new element in this chart section with the specified
        properties. Elements define the content structure and generation
        logic for chart sections.

        Args:
            order: Display order of the element (integer).
            element_type: Type identifier for the element (CHART_ELEMENT_TYPE enum).
            description: Description of the element.
            prompt: Generation prompt for the element content.
            for_each: Whether this element should be generated for each
                     waypoint (boolean).
            waypoints: Optional list of waypoint IDs associated with this element.
            metadata: Optional metadata dictionary for the element.
            **kwargs: Additional element properties.

        Returns:
            Created ChartElement instance.

        Raises:
            ApiError: If the API returns an error (e.g., validation error).
            AccQsureException: If there's an error making the request.
        """
        data = dict(
            order=order,
            type=(
                element_type.value
                if isinstance(element_type, CHART_ELEMENT_TYPE)
                else element_type
            ),
            description=description,
            prompt=prompt,
            for_each=for_each,
            waypoints=waypoints,
            metadata=metadata,
            **kwargs,
        )
        payload = {k: v for k, v in data.items() if v is not None}
        logging.info("Creating Chart Element %s", order)

        resp = await self.accqsure._query(
            f"/chart/{self.chart_id}/section/{self.section_id}/element",
            "POST",
            None,
            payload,
        )
        chart_element = ChartElement.from_api(
            self.accqsure, self.chart_id, self.section_id, resp
        )
        logging.info("Created Chart %s with id %s", order, chart_element.id)

        return chart_element

    async def remove(self, id_: str, **kwargs: Any) -> None:
        """Delete a chart element.

        Permanently deletes a chart element by its entity ID.

        Args:
            id_: Chart element entity ID (24-character string).
            **kwargs: Additional query parameters.

        Raises:
            ApiError: If the API returns an error (e.g., element not found).
            AccQsureException: If there's an error making the request.
        """
        await self.accqsure._query(
            f"/chart/{self.chart_id}/section/{self.section_id}/element/{id_}",
            "DELETE",
            {**kwargs},
        )


@dataclass
class ChartElement:
    """Represents an element within a chart section.

    Elements define the content structure and generation logic for
    chart sections. They can be associated with waypoints and contain
    metadata for customization.

    Attributes:
        chart_id: The chart ID this element belongs to.
        section_id: The section ID this element belongs to.
        id: Entity ID of the element.
        created_at: Creation timestamp.
        updated_at: Last update timestamp.
        order: Display order of the element.
        type: Element type (should be one of CHART_ELEMENT_TYPE enum values:
              'title', 'narrative', 'table', or 'static').
        description: Description of the element.
        prompt: Generation prompt for the element content.
        for_each: Whether this element should be generated for each waypoint.
        metadata: Optional metadata dictionary for the element.
        waypoints: Optional list of waypoints associated with this element.
    """

    chart_id: str
    section_id: str
    id: str
    created_at: str
    updated_at: str
    order: int
    type: str  # Should be one of CHART_ELEMENT_TYPE enum values
    description: str
    prompt: str
    for_each: bool
    metadata: Optional[Dict[str, Any]] = field(default=None)

    waypoints: Optional[List[ChartWaypoint]] = field(default=None)

    @classmethod
    def from_api(
        cls,
        accqsure: "AccQsure",
        chart_id: str,
        section_id: str,
        data: dict[str, Any],
    ) -> Optional["ChartElement"]:
        """Create a ChartElement instance from API response data.

        Args:
            accqsure: The AccQsure client instance.
            chart_id: The chart ID this element belongs to.
            section_id: The section ID this element belongs to.
            data: Dictionary containing chart element data from the API.

        Returns:
            ChartElement instance if data is provided, None otherwise.
        """
        if not data:
            return None
        entity = cls(
            chart_id=chart_id,
            section_id=section_id,
            id=data.get("entity_id"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
            order=data.get("order"),
            type=data.get("type"),
            description=data.get("description"),
            prompt=data.get("prompt"),
            for_each=data.get("for_each"),
            metadata=data.get("metadata"),
            waypoints=[
                ChartWaypoint.from_api(
                    accqsure=accqsure, chart_id=chart_id, data=waypoint
                )
                for waypoint in data.get("waypoints") or []
            ],
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

    async def refresh(self) -> "ChartElement":
        """Refresh the chart element data from the API.

        Fetches the latest chart element data from the API and updates the
        instance fields.

        Returns:
            Self for method chaining.

        Raises:
            ApiError: If the API returns an error.
            AccQsureException: If there's an error making the request.
        """
        resp = await self.accqsure._query(
            f"/chart/{self.chart_id}/section/{self.section_id}/element/{self.id}",
            "GET",
        )
        exclude = ["id", "chart_id", "section_id", "accqsure"]

        for f in fields(self.__class__):
            if (
                f.name not in exclude and f.init and resp.get(f.name)
            ):  # Only update init args (skip derived like sections/waypoints)
                setattr(self, f.name, resp.get(f.name))
        return self
