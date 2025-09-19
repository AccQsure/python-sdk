import json
import logging
from accqsure.exceptions import SpecificationError


class PlotMarkers(object):
    def __init__(
        self,
        accqsure,
        plot_id,
        plot_waypoint_id,
    ):
        self.accqsure = accqsure
        self.plot_id = plot_id
        self.waypoint_id = plot_waypoint_id

    async def get(self, id_, **kwargs):

        resp = await self.accqsure._query(
            f"/plot/{self.plot_id}/waypoint/{self.waypoint_id}/marker/{id_}",
            "GET",
            kwargs,
        )
        return PlotMarker(
            self.accqsure, self.plot_id, self.waypoint_id, **resp
        )

    async def list(self, limit=50, start_key=None, **kwargs):

        resp = await self.accqsure._query(
            f"/plot/{self.plot_id}/waypoint/{self.waypoint_id}/marker",
            "GET",
            {"limit": limit, "start_key": start_key, **kwargs},
        )
        plot_markers = [
            PlotMarker(
                self.accqsure, self.plot_id, self.waypoint_id, **plot_marker
            )
            for plot_marker in resp.get("results")
        ]
        return plot_markers, resp.get("last_key")

    async def create(
        self,
        name,
        contents,
        **kwargs,
    ):

        data = dict(
            name=name,
            contents=contents,
            **kwargs,
        )
        payload = {k: v for k, v in data.items() if v is not None}
        logging.info("Creating Plot Marker %s", name)

        resp = await self.accqsure._query(
            f"/plot/{self.plot_id}/waypoint/{self.waypoint_id}/marker",
            "POST",
            None,
            payload,
        )
        plot_marker = PlotMarker(
            self.accqsure, self.plot_id, self.waypoint_id, **resp
        )
        logging.info("Created Plot Marker %s with id %s", name, plot_marker.id)

        return plot_marker

    async def remove(self, id_, **kwargs):

        await self.accqsure._query(f"/plot/{id_}", "DELETE", {**kwargs})


class PlotMarker:
    def __init__(self, accqsure, plot_id, plot_waypoint_id, **kwargs):
        self.accqsure = accqsure
        self.plot_id = plot_id
        self.waypoint_id = plot_waypoint_id
        self._entity = kwargs
        self._id = self._entity.get("entity_id")
        self._name = self._entity.get("name")
        self._status = self._entity.get("status")
        self._content_id = self._entity.get("content_id")

    @property
    def id(self) -> str:
        return self._id

    @property
    def status(self) -> str:
        return self._status

    @property
    def name(self) -> str:
        return self._name

    def __str__(self):
        return json.dumps({k: v for k, v in self._entity.items()})

    def __repr__(self):
        return f"PlotMarker( accqsure , **{self._entity.__repr__()})"

    def __bool__(self):
        return bool(self._id)

    async def remove(self):

        await self.accqsure._query(
            f"/plot/{self.plot_id}/waypoint/{self.waypoint_id}/marker/{self._id}",
            "DELETE",
        )

    async def rename(self, name):

        resp = await self.accqsure._query(
            f"/plot/{self.plot_id}/waypoint/{self.waypoint_id}/marker/{self._id}",
            "PUT",
            None,
            dict(name=name),
        )
        self.__init__(self.accqsure, **resp)
        return self

    async def refresh(self):

        resp = await self.accqsure._query(
            f"/plot/{self.plot_id}/waypoint/{self.waypoint_id}/marker/{self.id}",
            "GET",
        )
        self.__init__(self.accqsure, **resp)
        return self

    async def _set_asset(self, path, file_name, mime_type, contents):
        return await self.accqsure._query(
            f"/plot/{self.plot_id}/waypoint/{self.waypoint_id}/marker/{self.id}/asset/{path}",
            "PUT",
            params={"file_name": file_name},
            data=contents,
            headers={"Content-Type": mime_type},
        )

    async def get_contents(self):
        if not self._content_id:
            raise SpecificationError(
                "content_id", "Content not ready for plot marker"
            )

        resp = await self.accqsure._query(
            f"/plot/{self.plot_id}/waypoint/{self.waypoint_id}/marker/{self.id}/asset/manifest.json",
            "GET",
        )
        return resp

    async def get_content_item(self, name):
        if not self._content_id:
            raise SpecificationError(
                "content_id", "Content not ready for plot marker"
            )

        return await self.accqsure._query(
            f"/plot/{self.plot_id}/waypoint/{self.waypoint_id}/marker/{self.id}/asset/{name}",
            "GET",
        )

    async def _set_content_item(self, name, file_name, mime_type, contents):
        if not self._content_id:
            raise SpecificationError(
                "content_id", "Content not ready for plot marker"
            )
        return await self._set_asset(name, file_name, mime_type, contents)
