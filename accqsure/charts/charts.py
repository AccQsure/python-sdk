from __future__ import annotations
from dataclasses import dataclass, field, fields
from typing import Optional, Any, TYPE_CHECKING
import logging

from accqsure.exceptions import SpecificationError
from accqsure.documents import Document
from .sections import ChartSections
from .waypoints import ChartWaypoints


if TYPE_CHECKING:
    from accqsure import AccQsure


@dataclass
class Charts:
    accqsure: "AccQsure" = field(repr=False, compare=False, hash=False)

    async def get(self, id_, **kwargs):

        resp = await self.accqsure._query(f"/chart/{id_}", "GET", kwargs)
        return Chart.from_api(self.accqsure, resp)

    async def list(
        self,
        document_type_id,
        limit=50,
        start_key=None,
        fetch_all=False,
        **kwargs,
    ):
        if fetch_all:
            resp = await self.accqsure._query_all(
                "/chart",
                "GET",
                {
                    "document_type_id": document_type_id,
                    **kwargs,
                },
            )
            charts = [
                Chart.from_api(self.accqsure, chart)
                for chart in resp.get("results")
            ]
            return charts, resp.get("last_key")
        else:
            resp = await self.accqsure._query(
                "/chart",
                "GET",
                {
                    "document_type_id": document_type_id,
                    "limit": limit,
                    "start_key": start_key,
                    **kwargs,
                },
            )
            charts = [
                Chart.from_api(self.accqsure, chart)
                for chart in resp.get("results")
            ]
            return charts, resp.get("last_key")

    async def create(
        self,
        name,
        document_type_id,
        reference_document_id,
        **kwargs,
    ):

        data = dict(
            name=name,
            document_type_id=document_type_id,
            reference_document_id=reference_document_id,
            **kwargs,
        )
        payload = {k: v for k, v in data.items() if v is not None}
        logging.info("Creating Chart %s", name)

        resp = await self.accqsure._query("/chart", "POST", None, payload)
        chart = Chart.from_api(self.accqsure, resp)
        logging.info("Created Chart %s with id %s", name, chart.id)

        return chart

    async def remove(self, id_, **kwargs):

        await self.accqsure._query(f"/chart/{id_}", "DELETE", {**kwargs})


@dataclass
class Chart:
    id: str
    name: str
    document_type_id: str
    status: str
    created_at: str
    updated_at: str
    reference_document: Optional[Document] = field(default=None)
    approved_by: Optional[str] = field(default=None)
    last_modified_by: Optional[str] = field(default=None)

    sections: ChartSections = field(
        init=False, repr=False, compare=False, hash=False
    )
    waypoints: ChartWaypoints = field(
        init=False, repr=False, compare=False, hash=False
    )

    @classmethod
    def from_api(cls, accqsure: "AccQsure", data: dict[str, Any]) -> "Chart":
        if not data:
            return None
        entity = cls(
            id=data.get("entity_id"),
            name=data.get("name"),
            status=data.get("status"),
            document_type_id=data.get("document_type_id"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
            reference_document=Document.from_api(
                accqsure=accqsure, data=data.get("reference_document")
            ),
            approved_by=data.get("approved_by"),
            last_modified_by=data.get("last_modified_by"),
        )
        entity.accqsure = accqsure
        entity.sections = ChartSections(entity.accqsure, entity.id)
        entity.waypoints = ChartWaypoints(entity.accqsure, entity.id)
        return entity

    @property
    def accqsure(self) -> "AccQsure":
        return self._accqsure

    @accqsure.setter
    def accqsure(self, value: "AccQsure"):
        self._accqsure = value

    async def remove(self):

        await self.accqsure._query(
            f"/chart/{self.id}",
            "DELETE",
        )

    async def rename(self, name):

        resp = await self.accqsure._query(
            f"/chart/{self.id}",
            "PUT",
            None,
            dict(name=name),
        )
        self.__init__(self.accqsure, **resp)
        return self

    async def refresh(self):

        resp = await self.accqsure._query(
            f"/chart/{self.id}",
            "GET",
        )
        exclude = ["id", "accqsure"]

        for f in fields(self.__class__):
            if (
                f.name not in exclude and f.init and resp.get(f.name)
            ):  # Only update init args (skip derived like sections/waypoints)
                setattr(self, f.name, resp.get(f.name))
        return self

    async def _set_asset(self, path, file_name, mime_type, contents):
        return await self.accqsure._query(
            f"/chart/{self.id}/asset/{path}",
            "PUT",
            params={"file_name": file_name},
            data=contents,
            headers={"Content-Type": mime_type},
        )

    async def get_reference_contents(self):
        if not self.reference_document:
            raise SpecificationError(
                "reference_document",
                "Reference document not found for chart",
            )
        document_id = self.reference_document.id
        content_id = self.reference_document.content_id
        if not content_id:
            raise SpecificationError(
                "content_id", "Content not uploaded for document"
            )
        resp = await self.accqsure._query(
            f"/document/{document_id}/asset/{content_id}/manifest.json",
            "GET",
        )
        return resp

    async def get_reference_content_item(self, name):
        if not self.reference_document:
            raise SpecificationError(
                "reference_document",
                "Reference document not found for chart",
            )
        document_id = self.reference_document.id
        content_id = self.reference_document.content_id
        if not content_id:
            raise SpecificationError(
                "content_id", "Content not uploaded for document"
            )
        resp = await self.accqsure._query(
            f"/document/{document_id}/asset/{content_id}/{name}",
            "GET",
        )
        return resp
