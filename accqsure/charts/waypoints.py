import json
import logging


class ChartWaypoints(object):
    def __init__(self, accqsure, chart_id):
        self.accqsure = accqsure
        self.chart_id = chart_id

    async def get(self, id_, **kwargs):

        resp = await self.accqsure._query(
            f"/chart/{self.chart_id}/waypoint/{id_}", "GET", kwargs
        )
        return ChartWaypoint(self.accqsure, self.chart_id, **resp)

    async def list(self, limit=50, start_key=None, **kwargs):

        resp = await self.accqsure._query(
            f"/chart/{self.chart_id}/waypoint",
            "GET",
            {"limit": limit, "start_key": start_key, **kwargs},
        )
        chart_waypoints = [
            ChartWaypoint(self.accqsure, self.chart_id, **chart_waypoint)
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
        chart_waypoint = ChartWaypoint(self.accqsure, **resp)
        logging.info(
            "Created Chart Waypoint %s with id %s", name, chart_waypoint.id
        )

        return chart_waypoint

    async def remove(self, id_, **kwargs):

        await self.accqsure._query(
            f"/chart/{self.chart_id}/waypoint/{id_}", "DELETE", {**kwargs}
        )


class ChartWaypoint:
    def __init__(self, accqsure, chart_id, **kwargs):
        self.accqsure = accqsure
        self.chart_id = chart_id
        self._entity = kwargs
        self._id = self._entity.get("entity_id")
        self._name = self._entity.get("name")

    @property
    def id(self) -> str:
        return self._id

    @property
    def name(self) -> str:
        return self._name

    def __str__(self):
        return json.dumps({k: v for k, v in self._entity.items()})

    def __repr__(self):
        return f"ChartWaypoint( accqsure , **{self._entity.__repr__()})"

    def __bool__(self):
        return bool(self._id)

    async def refresh(self):

        resp = await self.accqsure._query(
            f"/chart/{self.chart_id}/waypoint/{self.id}",
            "GET",
        )
        self.__init__(self.accqsure, **resp)
        return self
