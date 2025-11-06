from __future__ import annotations
from dataclasses import dataclass, field, fields
from typing import Optional, Any, TYPE_CHECKING
import logging

from accqsure.exceptions import SpecificationError

if TYPE_CHECKING:
    from accqsure import AccQsure


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
        return PlotMarker.from_api(
            self.accqsure, self.plot_id, self.waypoint_id, resp
        )

    async def list(self, limit=50, start_key=None, **kwargs):

        resp = await self.accqsure._query(
            f"/plot/{self.plot_id}/waypoint/{self.waypoint_id}/marker",
            "GET",
            {"limit": limit, "start_key": start_key, **kwargs},
        )
        plot_markers = [
            PlotMarker.from_api(
                self.accqsure, self.plot_id, self.waypoint_id, plot_marker
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
        plot_marker = PlotMarker.from_api(
            self.accqsure, self.plot_id, self.waypoint_id, resp
        )
        logging.info("Created Plot Marker %s with id %s", name, plot_marker.id)

        return plot_marker

    async def remove(self, id_, **kwargs):

        await self.accqsure._query(f"/plot/{id_}", "DELETE", {**kwargs})


@dataclass
class PlotMarker:
    plot_id: str
    waypoint_id: str
    id: str
    name: str
    status: str
    created_at: Optional[str] = field(default=None)
    updated_at: Optional[str] = field(default=None)
    content_id: Optional[str] = field(default=None)

    @classmethod
    def from_api(
        cls,
        accqsure: "AccQsure",
        plot_id: str,
        waypoint_id: str,
        data: dict[str, Any],
    ) -> "PlotMarker":
        if not data:
            return None
        entity = cls(
            plot_id=plot_id,
            waypoint_id=waypoint_id,
            id=data.get("entity_id"),
            name=data.get("name"),
            status=data.get("status"),
            content_id=data.get("content_id"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
        )
        entity.accqsure = accqsure
        return entity

    @property
    def accqsure(self) -> "AccQsure":
        return self._accqsure

    @accqsure.setter
    def accqsure(self, value: "AccQsure"):
        self._accqsure = value

    async def remove(self):

        await self.accqsure._query(
            f"/plot/{self.plot_id}/waypoint/{self.waypoint_id}/marker/{self.id}",
            "DELETE",
        )

    async def rename(self, name):

        resp = await self.accqsure._query(
            f"/plot/{self.plot_id}/waypoint/{self.waypoint_id}/marker/{self.id}",
            "PUT",
            None,
            dict(name=name),
        )
        exclude = ["id", "plot_id", "waypoint_id", "accqsure"]

        for f in fields(self.__class__):
            if (
                f.name not in exclude and f.init and resp.get(f.name) is not None
            ):  # Only update init args
                setattr(self, f.name, resp.get(f.name))
        return self

    async def refresh(self):

        resp = await self.accqsure._query(
            f"/plot/{self.plot_id}/waypoint/{self.waypoint_id}/marker/{self.id}",
            "GET",
        )
        exclude = ["id", "plot_id", "waypoint_id", "accqsure"]

        for f in fields(self.__class__):
            if (
                f.name not in exclude and f.init and resp.get(f.name) is not None
            ):  # Only update init args
                setattr(self, f.name, resp.get(f.name))
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
        if not self.content_id:
            raise SpecificationError(
                "content_id", "Content not ready for plot marker"
            )

        resp = await self.accqsure._query(
            f"/plot/{self.plot_id}/waypoint/{self.waypoint_id}/marker/{self.id}/asset/manifest.json",
            "GET",
        )
        return resp

    async def get_content_item(self, name):
        if not self.content_id:
            raise SpecificationError(
                "content_id", "Content not ready for plot marker"
            )

        return await self.accqsure._query(
            f"/plot/{self.plot_id}/waypoint/{self.waypoint_id}/marker/{self.id}/asset/{name}",
            "GET",
        )

    async def _set_content_item(self, name, file_name, mime_type, contents):
        if not self.content_id:
            raise SpecificationError(
                "content_id", "Content not ready for plot marker"
            )
        return await self._set_asset(name, file_name, mime_type, contents)
