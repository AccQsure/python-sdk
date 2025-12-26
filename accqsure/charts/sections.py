from __future__ import annotations
from dataclasses import dataclass, field, fields
import logging
from typing import Optional, Any, TYPE_CHECKING, List, Tuple

from accqsure.enums import CHART_SECTION_STYLE

if TYPE_CHECKING:
    from accqsure import AccQsure


from .elements import ChartElements


class ChartSections(object):
    """Manager for chart section resources.

    Provides methods to create, retrieve, list, and delete chart sections.
    Sections organize chart content hierarchically. Maps to the
    /v1/chart/{chart_id}/section API endpoints.
    """

    def __init__(self, accqsure: "AccQsure", chart_id: str) -> None:
        """Initialize the ChartSections manager.

        Args:
            accqsure: The AccQsure client instance.
            chart_id: The chart ID this manager is associated with.
        """
        self.accqsure = accqsure
        self.chart_id = chart_id

    async def get(self, id_: str, **kwargs: Any) -> Optional["ChartSection"]:
        """Get a chart section by ID.

        Retrieves a single chart section by its entity ID.

        Args:
            id_: Chart section entity ID (24-character string).
            **kwargs: Additional query parameters.

        Returns:
            ChartSection instance if found, None otherwise.

        Raises:
            ApiError: If the API returns an error.
            AccQsureException: If there's an error making the request.
        """
        resp = await self.accqsure._query(
            f"/chart/{self.chart_id}/section/{id_}", "GET", kwargs
        )
        return ChartSection.from_api(self.accqsure, self.chart_id, resp)

    async def list(
        self,
        limit: int = 50,
        start_key: Optional[str] = None,
        fetch_all: bool = False,
        **kwargs: Any,
    ) -> Union[List["ChartSection"], Tuple[List["ChartSection"], Optional[str]]]:
        """List chart sections.

        Retrieves a list of sections for this chart.
        Can return all results or paginated results.

        Args:
            limit: Number of results to return per page (default: 50, max: 100).
                   Only used if fetch_all is False.
            start_key: Pagination cursor from previous response.
                      Only used if fetch_all is False.
            fetch_all: If True, fetches all results across all pages.
                      If False, returns paginated results.
            **kwargs: Additional query parameters.

        Returns:
            If fetch_all is True: List of all ChartSection instances.
            If fetch_all is False: Tuple of (list of ChartSection instances,
                                          last_key for pagination).

        Raises:
            ApiError: If the API returns an error.
            AccQsureException: If there's an error making the request.
        """
        if fetch_all:
            resp = await self.accqsure._query_all(
                f"/chart/{self.chart_id}/section",
                "GET",
                {**kwargs},
            )
            chart_sections = [
                ChartSection.from_api(self.accqsure, self.chart_id, chart_section)
                for chart_section in resp
            ]
            return chart_sections
        else:
            resp = await self.accqsure._query(
                f"/chart/{self.chart_id}/section",
                "GET",
                {"limit": limit, "start_key": start_key, **kwargs},
            )
            chart_sections = [
                ChartSection.from_api(self.accqsure, self.chart_id, chart_section)
                for chart_section in resp.get("results")
            ]
            return chart_sections, resp.get("last_key")

    async def create(
        self,
        heading: str,
        style: CHART_SECTION_STYLE,
        order: int,
        number: Optional[str] = None,
        **kwargs: Any,
    ) -> "ChartSection":
        """Create a new chart section.

        Creates a new section in this chart with the specified heading,
        style, and order.

        Args:
            heading: Section heading text.
            style: Section style identifier (CHART_SECTION_STYLE enum).
            order: Display order of the section (integer).
            number: Optional section number.
            **kwargs: Additional section properties.

        Returns:
            Created ChartSection instance.

        Raises:
            ApiError: If the API returns an error (e.g., validation error).
            AccQsureException: If there's an error making the request.
        """
        data = dict(
            heading=heading,
            style=(
                style.value
                if isinstance(style, CHART_SECTION_STYLE)
                else style
            ),
            order=order,
            number=number,
            **kwargs,
        )
        payload = {k: v for k, v in data.items() if v is not None}
        logging.info("Creating Chart Section %s", order)

        resp = await self.accqsure._query(
            f"/chart/{self.chart_id}/section", "POST", None, payload
        )
        chart_section = ChartSection.from_api(
            self.accqsure, self.chart_id, resp
        )
        logging.info(
            "Created Chart Section %s with id %s", order, chart_section.id
        )

        return chart_section

    async def remove(self, id_: str, **kwargs: Any) -> None:
        """Delete a chart section.

        Permanently deletes a chart section by its entity ID.

        Args:
            id_: Chart section entity ID (24-character string).
            **kwargs: Additional query parameters.

        Raises:
            ApiError: If the API returns an error (e.g., section not found).
            AccQsureException: If there's an error making the request.
        """
        await self.accqsure._query(
            f"/chart/{self.chart_id}/section/{id_}", "DELETE", {**kwargs}
        )


@dataclass
class ChartSection:
    """Represents a section within a chart.

    Sections organize chart content hierarchically. Each section has
    a heading, style, order, and can contain elements.

    Attributes:
        chart_id: The chart ID this section belongs to.
        id: Entity ID of the section.
        created_at: Creation timestamp.
        updated_at: Last update timestamp.
        heading: Section heading text.
        style: Section style (should be one of CHART_SECTION_STYLE enum values:
               'title', 'h1', 'h2', 'h3', 'h4', 'h5', or 'h6').
        order: Display order of the section.
        number: Optional section number.
    """

    chart_id: str
    id: str
    created_at: str
    updated_at: str
    heading: str
    style: str  # Should be one of CHART_SECTION_STYLE enum values
    order: int
    number: Optional[str] = field(default=None)

    elements: ChartElements = field(
        init=False, repr=False, compare=False, hash=False
    )

    @classmethod
    def from_api(
        cls, accqsure: "AccQsure", chart_id: str, data: dict[str, Any]
    ) -> Optional["ChartSection"]:
        """Create a ChartSection instance from API response data.

        Args:
            accqsure: The AccQsure client instance.
            chart_id: The chart ID this section belongs to.
            data: Dictionary containing chart section data from the API.

        Returns:
            ChartSection instance if data is provided, None otherwise.
        """
        if not data:
            return None
        entity = cls(
            chart_id=chart_id,
            id=data.get("entity_id"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
            heading=data.get("heading"),
            number=data.get("number"),
            style=data.get("style"),
            order=data.get("order"),
        )
        entity.accqsure = accqsure
        entity.elements = ChartElements(
            entity.accqsure, entity.chart_id, entity.id
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

    async def refresh(self) -> "ChartSection":
        """Refresh the chart section data from the API.

        Fetches the latest chart section data from the API and updates the
        instance fields.

        Returns:
            Self for method chaining.

        Raises:
            ApiError: If the API returns an error.
            AccQsureException: If there's an error making the request.
        """
        resp = await self.accqsure._query(
            f"/chart/{self.chart_id}/section/{self.id}",
            "GET",
        )
        exclude = ["id", "chart_id", "accqsure"]

        for f in fields(self.__class__):
            if (
                f.name not in exclude and f.init and resp.get(f.name)
            ):  # Only update init args (skip derived like sections/waypoints)
                setattr(self, f.name, resp.get(f.name))

        return self
