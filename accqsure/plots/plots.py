import json
import logging
from accqsure.exceptions import SpecificationError
from .sections import PlotSections
from .waypoints import PlotWaypoints


class Plots(object):
    def __init__(self, accqsure):
        self.accqsure = accqsure

    async def get(self, id_, **kwargs):

        resp = await self.accqsure._query(f"/plot/{id_}", "GET", kwargs)
        return Plot(self.accqsure, **resp)

    async def list(self, limit=50, start_key=None, **kwargs):

        resp = await self.accqsure._query(
            "/plot",
            "GET",
            {"limit": limit, "start_key": start_key, **kwargs},
        )
        plots = [Plot(self.accqsure, **plot) for plot in resp.get("results")]
        return plots, resp.get("last_key")

    async def create(
        self,
        name,
        record_id,
        chart_id,
        **kwargs,
    ):

        data = dict(
            name=name,
            record_id=record_id,
            chart_id=chart_id,
            **kwargs,
        )
        payload = {k: v for k, v in data.items() if v is not None}
        logging.info("Creating Plot %s", name)

        resp = await self.accqsure._query("/plot", "POST", None, payload)
        plot = Plot(self.accqsure, **resp)
        logging.info("Created Plot %s with id %s", name, plot.id)

        return plot

    async def remove(self, id_, **kwargs):

        await self.accqsure._query(f"/plot/{id_}", "DELETE", {**kwargs})


class Plot:
    def __init__(self, accqsure, **kwargs):
        self.accqsure = accqsure
        self._entity = kwargs
        self._id = self._entity.get("entity_id")
        self._name = self._entity.get("name")
        self._record_id = self._entity.get("record_id")
        self._status = self._entity.get("status")
        self._content_id = self._entity.get("content_id")
        self.sections = PlotSections(self.accqsure, self._id)
        self.waypoints = PlotWaypoints(self.accqsure, self._id)

    @property
    def id(self) -> str:
        return self._id

    @property
    def record_id(self) -> str:
        return self._record_id

    @property
    def status(self) -> str:
        return self._status

    @property
    def name(self) -> str:
        return self._name

    def __str__(self):
        return json.dumps({k: v for k, v in self._entity.items()})

    def __repr__(self):
        return f"Plot( accqsure , **{self._entity.__repr__()})"

    def __bool__(self):
        return bool(self._id)

    async def remove(self):

        await self.accqsure._query(
            f"/plot/{self._id}",
            "DELETE",
        )

    async def rename(self, name):

        resp = await self.accqsure._query(
            f"/plot/{self._id}",
            "PUT",
            None,
            dict(name=name),
        )
        self.__init__(self.accqsure, **resp)
        return self

    async def refresh(self):

        resp = await self.accqsure._query(
            f"/plot/{self.id}",
            "GET",
        )
        self.__init__(self.accqsure, **resp)
        return self

    async def _set_asset(self, path, file_name, mime_type, contents):
        return await self.accqsure._query(
            f"/plot/{self.id}/asset/{path}",
            "PUT",
            params={"file_name": file_name},
            data=contents,
            headers={"Content-Type": mime_type},
        )

    async def get_contents(self):
        if not self._content_id:
            raise SpecificationError(
                "content_id", "Content not finalized for plot"
            )

        resp = await self.accqsure._query(
            f"/plot/{self.id}/asset/manifest.json",
            "GET",
        )
        return resp

    async def get_content_item(self, name):
        if not self._content_id:
            raise SpecificationError(
                "content_id", "Content not finalized for plot"
            )

        return await self.accqsure._query(
            f"/plot/{self.id}/asset/{name}",
            "GET",
        )

    async def _set_content_item(self, name, file_name, mime_type, contents):
        if not self._content_id:
            raise SpecificationError(
                "content_id", "Content not finalized for plot"
            )
        return await self._set_asset(f"{name}", file_name, mime_type, contents)
