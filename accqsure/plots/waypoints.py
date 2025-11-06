from __future__ import annotations
from dataclasses import dataclass, field, fields
from typing import Optional, Any, TYPE_CHECKING

from .markers import PlotMarkers

if TYPE_CHECKING:
    from accqsure import AccQsure


class PlotWaypoints(object):
    def __init__(self, accqsure, plot_id):
        self.accqsure = accqsure
        self.plot_id = plot_id

    async def get(self, id_, **kwargs):

        resp = await self.accqsure._query(
            f"/plot/{self.plot_id}/waypoint/{id_}", "GET", kwargs
        )
        return PlotWaypoint.from_api(self.accqsure, self.plot_id, resp)

    async def list(self, limit=50, start_key=None, **kwargs):

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
    ) -> "PlotWaypoint":
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
        return self._accqsure

    @accqsure.setter
    def accqsure(self, value: "AccQsure"):
        self._accqsure = value

    async def refresh(self):

        resp = await self.accqsure._query(
            f"/plot/{self.plot_id}/waypoint/{self.id}",
            "GET",
        )
        exclude = ["id", "plot_id", "accqsure"]

        for f in fields(self.__class__):
            if (
                f.name not in exclude and f.init and resp.get(f.name) is not None
            ):  # Only update init args (skip derived like markers)
                setattr(self, f.name, resp.get(f.name))
        return self
