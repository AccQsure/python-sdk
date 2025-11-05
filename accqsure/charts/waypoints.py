from __future__ import annotations
from dataclasses import dataclass, field, fields
import logging
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from accqsure import AccQsure


@dataclass
class ChartWaypoints(object):
    accqsure: "AccQsure" = field(repr=False, compare=False, hash=False)
    chart_id: str

    async def get(self, id_, **kwargs):

        resp = await self.accqsure._query(
            f"/chart/{self.chart_id}/waypoint/{id_}", "GET", kwargs
        )
        return ChartWaypoint.from_api(self.accqsure, self.chart_id, resp)

    async def list(self, limit=50, start_key=None, **kwargs):

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
        name,
        **kwargs,
    ):

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

    async def remove(self, id_, **kwargs):

        await self.accqsure._query(
            f"/chart/{self.chart_id}/waypoint/{id_}", "DELETE", {**kwargs}
        )


@dataclass
class ChartWaypoint:
    accqsure: "AccQsure" = field(repr=False, compare=False, hash=False)
    chart_id: str
    id: str
    name: str
    created_at: str
    updated_at: str

    @classmethod
    def from_api(
        cls, accqsure: "AccQsure", chart_id: str, data: dict[str, Any]
    ) -> "ChartWaypoint":
        if not data:
            return None
        return cls(
            accqsure=accqsure,
            chart_id=chart_id,
            id=data.get("entity_id"),
            name=data.get("name"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
        )

    async def refresh(self):

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
