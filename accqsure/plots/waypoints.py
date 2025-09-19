import json
from .markers import PlotMarkers


class PlotWaypoints(object):
    def __init__(self, accqsure, plot_id):
        self.accqsure = accqsure
        self.plot_id = plot_id

    async def get(self, id_, **kwargs):

        resp = await self.accqsure._query(
            f"/plot/{self.plot_id}/waypoint/{id_}", "GET", kwargs
        )
        return PlotWaypoint(self.accqsure, self.plot_id, **resp)

    async def list(self, limit=50, start_key=None, **kwargs):

        resp = await self.accqsure._query(
            f"/plot/{self.plot_id}/waypoint",
            "GET",
            {"limit": limit, "start_key": start_key, **kwargs},
        )
        plot_waypoints = [
            PlotWaypoint(self.accqsure, self.plot_id, **plot_waypoint)
            for plot_waypoint in resp.get("results")
        ]
        return plot_waypoints, resp.get("last_key")


class PlotWaypoint:
    def __init__(self, accqsure, plot_id, **kwargs):
        self.accqsure = accqsure
        self.plot_id = plot_id
        self._entity = kwargs
        self._id = self._entity.get("entity_id")
        self._name = self._entity.get("name")
        self.markers = PlotMarkers(self.accqsure, self.plot_id, self._id)

    @property
    def id(self) -> str:
        return self._id

    @property
    def name(self) -> str:
        return self._name

    def __str__(self):
        return json.dumps({k: v for k, v in self._entity.items()})

    def __repr__(self):
        return f"PlotWaypoint( accqsure , **{self._entity.__repr__()})"

    def __bool__(self):
        return bool(self._id)

    async def refresh(self):

        resp = await self.accqsure._query(
            f"/plot/{self.plot_id}/waypoint/{self.id}",
            "GET",
        )
        self.__init__(self.accqsure, **resp)
        return self
