from __future__ import annotations
from dataclasses import dataclass, field, fields
from typing import Optional, Any, TYPE_CHECKING
import logging

from accqsure.exceptions import SpecificationError
from .sections import PlotSections
from .waypoints import PlotWaypoints

if TYPE_CHECKING:
    from accqsure import AccQsure


class Plots(object):
    def __init__(self, accqsure):
        self.accqsure = accqsure

    async def get(self, id_, **kwargs):

        resp = await self.accqsure._query(f"/plot/{id_}", "GET", kwargs)
        return Plot.from_api(self.accqsure, resp)

    async def list(self, limit=50, start_key=None, **kwargs):

        resp = await self.accqsure._query(
            "/plot",
            "GET",
            {"limit": limit, "start_key": start_key, **kwargs},
        )
        plots = [Plot.from_api(self.accqsure, plot) for plot in resp.get("results")]
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
        plot = Plot.from_api(self.accqsure, resp)
        logging.info("Created Plot %s with id %s", name, plot.id)

        return plot

    async def remove(self, id_, **kwargs):

        await self.accqsure._query(f"/plot/{id_}", "DELETE", {**kwargs})


@dataclass
class Plot:
    id: str
    name: str
    record_id: str
    status: str
    created_at: Optional[str] = field(default=None)
    updated_at: Optional[str] = field(default=None)
    content_id: Optional[str] = field(default=None)

    sections: PlotSections = field(
        init=False, repr=False, compare=False, hash=False
    )
    waypoints: PlotWaypoints = field(
        init=False, repr=False, compare=False, hash=False
    )

    @classmethod
    def from_api(
        cls, accqsure: "AccQsure", data: dict[str, Any]
    ) -> "Plot":
        if not data:
            return None
        entity = cls(
            id=data.get("entity_id"),
            name=data.get("name"),
            record_id=data.get("record_id"),
            status=data.get("status"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
            content_id=data.get("content_id"),
        )
        entity.accqsure = accqsure
        entity.sections = PlotSections(entity.accqsure, entity.id)
        entity.waypoints = PlotWaypoints(entity.accqsure, entity.id)
        return entity

    @property
    def accqsure(self) -> "AccQsure":
        return self._accqsure

    @accqsure.setter
    def accqsure(self, value: "AccQsure"):
        self._accqsure = value

    async def remove(self):

        await self.accqsure._query(
            f"/plot/{self.id}",
            "DELETE",
        )

    async def rename(self, name):

        resp = await self.accqsure._query(
            f"/plot/{self.id}",
            "PUT",
            None,
            dict(name=name),
        )
        exclude = ["id", "accqsure"]

        for f in fields(self.__class__):
            if (
                f.name not in exclude and f.init and resp.get(f.name) is not None
            ):  # Only update init args (skip derived like sections/waypoints)
                setattr(self, f.name, resp.get(f.name))
        return self

    async def refresh(self):

        resp = await self.accqsure._query(
            f"/plot/{self.id}",
            "GET",
        )
        exclude = ["id", "accqsure"]

        for f in fields(self.__class__):
            if (
                f.name not in exclude and f.init and resp.get(f.name) is not None
            ):  # Only update init args (skip derived like sections/waypoints)
                setattr(self, f.name, resp.get(f.name))
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
        if not self.content_id:
            raise SpecificationError(
                "content_id", "Content not finalized for plot"
            )

        resp = await self.accqsure._query(
            f"/plot/{self.id}/asset/manifest.json",
            "GET",
        )
        return resp

    async def get_content_item(self, name):
        if not self.content_id:
            raise SpecificationError(
                "content_id", "Content not finalized for plot"
            )

        return await self.accqsure._query(
            f"/plot/{self.id}/asset/{name}",
            "GET",
        )

    async def _set_content_item(self, name, file_name, mime_type, contents):
        if not self.content_id:
            raise SpecificationError(
                "content_id", "Content not finalized for plot"
            )
        return await self._set_asset(f"{name}", file_name, mime_type, contents)
