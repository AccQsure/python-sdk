from __future__ import annotations
from dataclasses import dataclass, fields
import logging
from typing import Any, TYPE_CHECKING, List, Tuple, Optional

if TYPE_CHECKING:
    from accqsure import AccQsure


class ChartWaypoints(object):
    """Manager for chart waypoint resources.

    Provides methods to create, retrieve, list, and delete chart waypoints.
    Waypoints are reference points used in chart elements.
    """

    def __init__(self, accqsure: "AccQsure", chart_id: str) -> None:
        """Initialize the ChartWaypoints manager.

        Args:
            accqsure: The AccQsure client instance.
            chart_id: The chart ID this manager is associated with.
        """
        self.accqsure = accqsure
        self.chart_id = chart_id

    async def get(self, id_: str, **kwargs: Any) -> Optional["ChartWaypoint"]:
        """Get a chart waypoint by ID.

        Retrieves a single chart waypoint by its entity ID.

        Args:
            id_: Chart waypoint entity ID (24-character string).
            **kwargs: Additional query parameters.

        Returns:
            ChartWaypoint instance if found, None otherwise.

        Raises:
            ApiError: If the API returns an error.
            AccQsureException: If there's an error making the request.
        """
        resp = await self.accqsure._query(
            f"/chart/{self.chart_id}/waypoint/{id_}", "GET", kwargs
        )
        return ChartWaypoint.from_api(self.accqsure, self.chart_id, resp)

    async def list(
        self,
        limit: int = 50,
        start_key: Optional[str] = None,
        **kwargs: Any,
    ) -> Tuple[List["ChartWaypoint"], Optional[str]]:
        """List chart waypoints.

        Retrieves a paginated list of waypoints for this chart.

        Args:
            limit: Number of results to return (default: 50, max: 100).
            start_key: Pagination cursor from previous response.
            **kwargs: Additional query parameters.

        Returns:
            Tuple of (list of ChartWaypoint instances, last_key for pagination).

        Raises:
            ApiError: If the API returns an error.
            AccQsureException: If there's an error making the request.
        """
        resp = await self.accqsure._query(
            f"/chart/{self.chart_id}/waypoint",
            "GET",
            {"limit": limit, "start_key": start_key, **kwargs},
        )
        chart_waypoints = [
            ChartWaypoint.from_api(
                self.accqsure, self.chart_id, chart_waypoint
            )
            for chart_waypoint in resp.get("results")
        ]
        return chart_waypoints, resp.get("last_key")

    async def create(
        self,
        name: str,
        **kwargs: Any,
    ) -> "ChartWaypoint":
        """Create a new chart waypoint.

        Creates a new waypoint in this chart with the specified name.

        Args:
            name: Name of the waypoint.
            **kwargs: Additional waypoint properties.

        Returns:
            Created ChartWaypoint instance.

        Raises:
            ApiError: If the API returns an error (e.g., validation error).
            AccQsureException: If there's an error making the request.
        """
        data = dict(
            name=name,
            **kwargs,
        )
        payload = {k: v for k, v in data.items() if v is not None}
        logging.info("Creating Chart Waypoint %s", name)

        resp = await self.accqsure._query(
            f"/chart/{self.chart_id}/waypoint", "POST", None, payload
        )
        chart_waypoint = ChartWaypoint.from_api(
            self.accqsure, self.chart_id, resp
        )
        logging.info(
            "Created Chart Waypoint %s with id %s", name, chart_waypoint.id
        )

        return chart_waypoint

    async def remove(self, id_: str, **kwargs: Any) -> None:
        """Delete a chart waypoint.

        Permanently deletes a chart waypoint by its entity ID.

        Args:
            id_: Chart waypoint entity ID (24-character string).
            **kwargs: Additional query parameters.

        Raises:
            ApiError: If the API returns an error (e.g., waypoint not found).
            AccQsureException: If there's an error making the request.
        """
        await self.accqsure._query(
            f"/chart/{self.chart_id}/waypoint/{id_}", "DELETE", {**kwargs}
        )


@dataclass
class ChartWaypoint:
    """Represents a waypoint within a chart.

    Waypoints are reference points used in chart elements to mark
    specific locations or data points.
    """

    chart_id: str
    id: str
    name: str
    created_at: str
    updated_at: str

    @classmethod
    def from_api(
        cls, accqsure: "AccQsure", chart_id: str, data: dict[str, Any]
    ) -> Optional["ChartWaypoint"]:
        """Create a ChartWaypoint instance from API response data.

        Args:
            accqsure: The AccQsure client instance.
            chart_id: The chart ID this waypoint belongs to.
            data: Dictionary containing chart waypoint data from the API.

        Returns:
            ChartWaypoint instance if data is provided, None otherwise.
        """
        if not data:
            return None

        entity = cls(
            chart_id=chart_id,
            id=data.get("entity_id"),
            name=data.get("name"),
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

    async def refresh(self) -> "ChartWaypoint":
        """Refresh the chart waypoint data from the API.

        Fetches the latest chart waypoint data from the API and updates the
        instance fields.

        Returns:
            Self for method chaining.

        Raises:
            ApiError: If the API returns an error.
            AccQsureException: If there's an error making the request.
        """
        resp = await self.accqsure._query(
            f"/chart/{self.chart_id}/waypoint/{self.id}",
            "GET",
        )
        exclude = ["id", "chart_id", "accqsure"]

        for f in fields(self.__class__):
            if (
                f.name not in exclude and f.init and resp.get(f.name)
            ):  # Only update init args (skip derived like sections/waypoints)
                setattr(self, f.name, resp.get(f.name))

        return self
