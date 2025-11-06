from __future__ import annotations
from dataclasses import dataclass, field, fields
from typing import Optional, Any, TYPE_CHECKING
import logging

from accqsure.exceptions import SpecificationError

if TYPE_CHECKING:
    from accqsure import AccQsure


class Inspections(object):
    def __init__(self, accqsure):

        self.accqsure = accqsure

    async def get(self, id_, **kwargs):

        resp = await self.accqsure._query(f"/inspection/{id_}", "GET", kwargs)
        return Inspection.from_api(self.accqsure, resp)

    async def list(self, inspection_type, limit=50, start_key=None, **kwargs):

        resp = await self.accqsure._query(
            "/inspection",
            "GET",
            {
                "type": inspection_type,
                "limit": limit,
                "start_key": start_key,
                **kwargs,
            },
        )
        inspections = [
            Inspection.from_api(self.accqsure, inspection)
            for inspection in resp.get("results")
        ]
        return inspections, resp.get("last_key")

    async def create(
        self,
        inspection_type,
        name,
        document_type_id,
        manifests,
        draft=None,
        documents=None,
        **kwargs,
    ):

        data = dict(
            name=name,
            type=inspection_type,
            document_type_id=document_type_id,
            manifests=manifests,
            draft=draft,
            documents=documents,
            **kwargs,
        )
        payload = {k: v for k, v in data.items() if v is not None}
        logging.info("Creating Inspection %s", name)

        resp = await self.accqsure._query("/inspection", "POST", None, payload)
        inspection = Inspection.from_api(self.accqsure, resp)
        logging.info("Created Inspection %s with id %s", name, inspection.id)

        return inspection

    async def remove(self, id_, **kwargs):

        await self.accqsure._query(f"/inspection/{id_}", "DELETE", {**kwargs})


@dataclass
class Inspection:
    id: str
    name: str
    type: str
    status: str
    created_at: Optional[str] = field(default=None)
    updated_at: Optional[str] = field(default=None)
    document_type_id: Optional[str] = field(default=None)
    doc_content_id: Optional[str] = field(default=None)
    content_id: Optional[str] = field(default=None)

    @classmethod
    def from_api(
        cls, accqsure: "AccQsure", data: dict[str, Any]
    ) -> "Inspection":
        if not data:
            return None
        entity = cls(
            id=data.get("entity_id"),
            name=data.get("name"),
            type=data.get("type"),
            status=data.get("status"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
            document_type_id=data.get("document_type_id"),
            doc_content_id=data.get("doc_content_id"),
            content_id=data.get("content_id"),
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
            f"/inspection/{self.id}",
            "DELETE",
        )

    async def rename(self, name):

        resp = await self.accqsure._query(
            f"/inspection/{self.id}",
            "PUT",
            None,
            dict(name=name),
        )
        exclude = ["id", "accqsure"]

        for f in fields(self.__class__):
            if (
                f.name not in exclude and f.init and resp.get(f.name) is not None
            ):  # Only update init args
                setattr(self, f.name, resp.get(f.name))
        return self

    async def run(self):

        resp = await self.accqsure._query(
            f"/inspection/{self.id}/run",
            "POST",
        )
        exclude = ["id", "accqsure"]

        for f in fields(self.__class__):
            if (
                f.name not in exclude and f.init and resp.get(f.name) is not None
            ):  # Only update init args
                setattr(self, f.name, resp.get(f.name))
        return self

    async def refresh(self):

        resp = await self.accqsure._query(
            f"/inspection/{self.id}",
            "GET",
        )
        exclude = ["id", "accqsure"]

        for f in fields(self.__class__):
            if (
                f.name not in exclude and f.init and resp.get(f.name) is not None
            ):  # Only update init args
                setattr(self, f.name, resp.get(f.name))
        return self

    async def _set_asset(self, path, file_name, mime_type, contents):
        return await self.accqsure._query(
            f"/inspection/{self.id}/asset/{path}",
            "PUT",
            params={"file_name": file_name},
            data=contents,
            headers={"Content-Type": mime_type},
        )

    async def get_doc_contents(self):
        if not self.doc_content_id:
            raise SpecificationError(
                "doc_content_id",
                "Document content not uploaded for inspection",
            )

        resp = await self.accqsure._query(
            f"/inspection/{self.id}/asset/{self.doc_content_id}/manifest.json",
            "GET",
        )
        return resp

    async def get_doc_content_item(self, name):
        if not self.doc_content_id:
            raise SpecificationError(
                "doc_content_id", "Document not uploaded for inspection"
            )

        return await self.accqsure._query(
            f"/inspection/{self.id}/asset/{self.doc_content_id}/{name}",
            "GET",
        )

    async def _set_doc_content_item(
        self, name, file_name, mime_type, contents
    ):
        if not self.doc_content_id:
            raise SpecificationError(
                "content_id", "Content not finalized for inspection"
            )
        return await self._set_asset(
            f"{self.doc_content_id}/{name}", file_name, mime_type, contents
        )

    async def get_contents(self):
        if not self.content_id:
            raise SpecificationError(
                "content_id", "Content not finalized for inspection"
            )

        resp = await self.accqsure._query(
            f"/inspection/{self.id}/asset/{self.content_id}/manifest.json",
            "GET",
        )
        return resp

    async def get_content_item(self, name):
        if not self.content_id:
            raise SpecificationError(
                "content_id", "Content not finalized for inspection"
            )

        return await self.accqsure._query(
            f"/inspection/{self.id}/asset/{self.content_id}/{name}",
            "GET",
        )

    async def _set_content_item(self, name, file_name, mime_type, contents):
        if not self.content_id:
            raise SpecificationError(
                "content_id", "Content not finalized for inspection"
            )
        return await self._set_asset(
            f"{self.content_id}/{name}", file_name, mime_type, contents
        )

    async def download_report(self):
        if not self.content_id:
            raise SpecificationError(
                "content_id", "Content not finalized for inspection"
            )
        manifest = await self.get_contents()
        return await self.get_content_item(manifest.get("report"))

    async def list_checks(
        self,
        document_id=None,
        manifest_id=None,
        limit=50,
        start_key=None,
        name=None,
        **kwargs,
    ):

        resp = await self.accqsure._query(
            f"/inspection/{self.id}/check",
            "GET",
            {
                "document_id": document_id,
                "manifest_id": manifest_id,
                "limit": limit,
                "start_key": start_key,
                "name": name,
                **kwargs,
            },
        )
        checks = [
            InspectionCheck.from_api(self.accqsure, self.id, check)
            for check in resp.get("results")
        ]
        return checks, resp.get("last_key")


@dataclass
class InspectionCheck:
    inspection_id: str
    id: str
    section: str
    name: str
    status: str
    critical: Optional[bool] = field(default=None)
    compliant: Optional[bool] = field(default=None)
    rationale: Optional[str] = field(default=None)
    suggestion: Optional[str] = field(default=None)
    created_at: Optional[str] = field(default=None)
    updated_at: Optional[str] = field(default=None)

    @classmethod
    def from_api(
        cls, accqsure: "AccQsure", inspection_id: str, data: dict[str, Any]
    ) -> "InspectionCheck":
        if not data:
            return None
        entity = cls(
            inspection_id=inspection_id,
            id=data.get("entity_id"),
            section=data.get("check_section"),
            name=data.get("check_name"),
            status=data.get("status"),
            critical=data.get("critical"),
            compliant=data.get("compliant"),
            rationale=data.get("rationale"),
            suggestion=data.get("suggestion"),
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

    async def update(self, **kwargs):

        resp = await self.accqsure._query(
            f"/inspection/{self.inspection_id}/check/{self.id}",
            "PUT",
            None,
            dict(**kwargs),
        )
        exclude = ["id", "inspection_id", "accqsure"]

        for f in fields(self.__class__):
            if (
                f.name not in exclude and f.init and resp.get(f.name) is not None
            ):  # Only update init args
                # Handle field name mapping
                field_name = f.name
                if field_name == "section":
                    setattr(self, field_name, resp.get("check_section"))
                elif field_name == "name":
                    setattr(self, field_name, resp.get("check_name"))
                else:
                    setattr(self, field_name, resp.get(field_name))
        return self

    async def refresh(self):

        resp = await self.accqsure._query(
            f"/inspection/{self.inspection_id}/check/{self.id}",
            "GET",
        )
        exclude = ["id", "inspection_id", "accqsure"]

        for f in fields(self.__class__):
            if (
                f.name not in exclude and f.init and resp.get(f.name) is not None
            ):  # Only update init args
                # Handle field name mapping
                field_name = f.name
                if field_name == "section":
                    setattr(self, field_name, resp.get("check_section"))
                elif field_name == "name":
                    setattr(self, field_name, resp.get("check_name"))
                else:
                    setattr(self, field_name, resp.get(field_name))
        return self
