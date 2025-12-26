from __future__ import annotations
from dataclasses import dataclass, field, fields
from typing import Optional, Any, TYPE_CHECKING, List, Tuple

from .markers import PlotMarkers

if TYPE_CHECKING:
    from accqsure import AccQsure


class PlotWaypoints(object):
    """Manager for plot waypoint resources.

    Provides methods to retrieve and list plot waypoints.
    Waypoints are buckets of reference contents for plot elements.
    """

    def __init__(self, accqsure: "AccQsure", plot_id: str) -> None:
        """Initialize the PlotWaypoints manager.

        Args:
            accqsure: The AccQsure client instance.
            plot_id: The plot ID this manager is associated with.
        """
        self.accqsure = accqsure
        self.plot_id = plot_id

    async def get(self, id_: str, **kwargs: Any) -> Optional["PlotWaypoint"]:
        """Get a plot waypoint by ID.

        Retrieves a single plot waypoint by its entity ID.

        Args:
            id_: Plot waypoint entity ID (24-character string).
            **kwargs: Additional query parameters.

        Returns:
            PlotWaypoint instance if found, None otherwise.

        Raises:
            ApiError: If the API returns an error.
            AccQsureException: If there's an error making the request.
        """
        resp = await self.accqsure._query(
            f"/plot/{self.plot_id}/waypoint/{id_}", "GET", kwargs
        )
        return PlotWaypoint.from_api(self.accqsure, self.plot_id, resp)

    async def list(
        self,
        limit: int = 50,
        start_key: Optional[str] = None,
        **kwargs: Any,
    ) -> Tuple[List["PlotWaypoint"], Optional[str]]:
        """List plot waypoints.

        Retrieves a paginated list of waypoints for this plot.

        Args:
            limit: Number of results to return (default: 50, max: 100).
            start_key: Pagination cursor from previous response.
            **kwargs: Additional query parameters.

        Returns:
            Tuple of (list of PlotWaypoint instances, last_key for pagination).

        Raises:
            ApiError: If the API returns an error.
            AccQsureException: If there's an error making the request.
        """
        resp = await self.accqsure._query(
            f"/plot/{self.plot_id}/waypoint",
            "GET",
            {"limit": limit, "start_key": start_key, **kwargs},
        )
        plot_waypoints = [
            PlotWaypoint.from_api(self.accqsure, self.plot_id, plot_waypoint)
            for plot_waypoint in resp.get("results")
        ]
        return plot_waypoints, resp.get("last_key")


@dataclass
class PlotWaypoint:
    """Represents a waypoint within a plot.

    Waypoints are reference points used in plot elements to mark
    specific locations or data points. Each waypoint can have markers.
    """

    plot_id: str
    id: str
    name: str
    created_at: Optional[str] = field(default=None)
    updated_at: Optional[str] = field(default=None)

    markers: PlotMarkers = field(
        init=False, repr=False, compare=False, hash=False
    )

    @classmethod
    def from_api(
        cls, accqsure: "AccQsure", plot_id: str, data: dict[str, Any]
    ) -> Optional["PlotWaypoint"]:
        """Create a PlotWaypoint instance from API response data.

        Args:
            accqsure: The AccQsure client instance.
            plot_id: The plot ID this waypoint belongs to.
            data: Dictionary containing plot waypoint data from the API.

        Returns:
            PlotWaypoint instance if data is provided, None otherwise.
        """
        if not data:
            return None
        entity = cls(
            plot_id=plot_id,
            id=data.get("entity_id"),
            name=data.get("name"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
        )
        entity.accqsure = accqsure
        entity.markers = PlotMarkers(
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

    async def refresh(self) -> "PlotWaypoint":
        """Refresh the plot waypoint data from the API.

        Fetches the latest plot waypoint data from the API and updates the
        instance fields.

        Returns:
            Self for method chaining.

        Raises:
            ApiError: If the API returns an error.
            AccQsureException: If there's an error making the request.
        """
        resp = await self.accqsure._query(
            f"/plot/{self.plot_id}/waypoint/{self.id}",
            "GET",
        )
        exclude = ["id", "plot_id", "accqsure"]

        for f in fields(self.__class__):
            if (
                f.name not in exclude
                and f.init
                and resp.get(f.name) is not None
            ):  # Only update init args (skip derived like markers)
                setattr(self, f.name, resp.get(f.name))
        return self
