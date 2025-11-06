from __future__ import annotations
from dataclasses import dataclass, field, fields
from typing import Optional, Any, TYPE_CHECKING
import logging

from accqsure.exceptions import SpecificationError
from accqsure.documents import Document

if TYPE_CHECKING:
    from accqsure import AccQsure


class Manifests(object):
    def __init__(self, accqsure):
        self.accqsure = accqsure

    async def get(self, id_, **kwargs):
        resp = await self.accqsure._query(f"/manifest/{id_}", "GET", kwargs)
        return Manifest.from_api(self.accqsure, resp)

    async def get_global(self, **kwargs):
        resp = await self.accqsure._query("/manifest/global", "GET", kwargs)
        return Manifest.from_api(self.accqsure, resp)

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
                "/manifest",
                "GET",
                {
                    "document_type_id": document_type_id,
                    **kwargs,
                },
            )
            manifests = [
                Manifest.from_api(self.accqsure, manifest) for manifest in resp
            ]
            return manifests
        else:
            resp = await self.accqsure._query(
                "/manifest",
                "GET",
                {
                    "document_type_id": document_type_id,
                    "limit": limit,
                    "start_key": start_key,
                    **kwargs,
                },
            )
            manifests = [
                Manifest.from_api(self.accqsure, manifest)
                for manifest in resp.get("results")
            ]
            return manifests, resp.get("last_key")

    async def create(
        self,
        document_type_id,
        name,
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
        logging.info("Creating Manifest %s", name)
        resp = await self.accqsure._query("/manifest", "POST", None, payload)
        manifest = Manifest.from_api(self.accqsure, resp)
        logging.info("Created Manifest %s with id %s", name, manifest.id)

        return manifest

    async def remove(self, id_, **kwargs):
        await self.accqsure._query(
            f"/manifest/{id_}", "DELETE", dict(**kwargs)
        )


@dataclass
class Manifest:
    id: str
    name: str
    document_type_id: str
    created_at: str
    updated_at: str
    global_: Optional[bool] = field(default=None)
    reference_document: Optional[Document] = field(default=None)

    @classmethod
    def from_api(
        cls, accqsure: "AccQsure", data: dict[str, Any]
    ) -> "Manifest":
        if not data:
            return None
        entity = cls(
            id=data.get("entity_id"),
            name=data.get("name"),
            document_type_id=data.get("document_type_id"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
            global_=data.get("global"),
            reference_document=Document.from_api(
                accqsure=accqsure, data=data.get("reference_document")
            )
            if data.get("reference_document")
            else None,
        )
        entity.accqsure = accqsure
        return entity

    @property
    def accqsure(self) -> "AccQsure":
        return self._accqsure

    @accqsure.setter
    def accqsure(self, value: "AccQsure"):
        self._accqsure = value

    @property
    def reference_document_id(self) -> str:
        return (
            self.reference_document.id
            if self.reference_document
            else "UNKNOWN"
        )

    @property
    def reference_document_doc_id(self) -> str:
        return (
            self.reference_document.doc_id
            if self.reference_document
            else "UNKNOWN"
        )

    async def remove(self):
        await self.accqsure._query(
            f"/manifest/{self.id}",
            "DELETE",
        )

    async def rename(self, name):
        resp = await self.accqsure._query(
            f"/manifest/{self.id}",
            "PUT",
            None,
            dict(name=name),
        )
        exclude = ["id", "accqsure"]

        for f in fields(self.__class__):
            if (
                f.name not in exclude and f.init and resp.get(f.name)
            ):  # Only update init args
                setattr(self, f.name, resp.get(f.name))
        return self

    async def refresh(self):
        resp = await self.accqsure._query(
            f"/manifest/{self.id}",
            "GET",
        )
        exclude = ["id", "accqsure", "reference_document"]

        for f in fields(self.__class__):
            if (
                f.name not in exclude and f.init and resp.get(f.name) is not None
            ):  # Only update init args
                setattr(self, f.name, resp.get(f.name))
        
        # Handle reference_document separately
        if resp.get("reference_document"):
            self.reference_document = Document.from_api(
                accqsure=self.accqsure, data=resp.get("reference_document")
            )
        elif "reference_document" in resp:
            self.reference_document = None
        
        return self

    async def get_reference_contents(self):
        if not self.reference_document:
            raise SpecificationError(
                "reference_document",
                "Reference document not found for manifest",
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
                "Reference document not found for manifest",
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

    async def list_checks(self, limit=50, start_key=None, **kwargs):
        resp = await self.accqsure._query(
            f"/manifest/{self.id}/check",
            "GET",
            {"limit": limit, "start_key": start_key, **kwargs},
        )
        checks = [
            ManifestCheck.from_api(self.accqsure, self.id, check)
            for check in resp.get("results")
        ]
        return checks, resp.get("last_key")

    async def create_check(self, name, section, prompt, **kwargs):
        data = dict(
            name=name,
            section=section,
            prompt=prompt,
            **kwargs,
        )
        payload = {k: v for k, v in data.items() if v is not None}
        logging.info("Creating Manifest Check %s", name)
        resp = await self.accqsure._query(
            f"/manifest/{self.id}/check", "POST", None, payload
        )
        check = ManifestCheck.from_api(self.accqsure, self.id, resp)
        logging.info("Created Manifest Check %s with id %s", name, check.id)

        return check

    async def remove_check(self, check_id, **kwargs):
        await self.accqsure._query(
            f"/manifest/{self.id}/check/{check_id}", "DELETE", dict(**kwargs)
        )

    async def _set_asset(self, path, file_name, mime_type, contents):
        return await self.accqsure._query(
            f"/manifest/{self.id}/asset/{path}",
            "PUT",
            params={"file_name": file_name},
            data=contents,
            headers={"Content-Type": mime_type},
        )


@dataclass
class ManifestCheck:
    manifest_id: str
    id: str
    section: str
    name: str
    prompt: str
    critical: Optional[bool] = field(default=None)
    created_at: Optional[str] = field(default=None)
    updated_at: Optional[str] = field(default=None)

    @classmethod
    def from_api(
        cls, accqsure: "AccQsure", manifest_id: str, data: dict[str, Any]
    ) -> "ManifestCheck":
        if not data:
            return None
        entity = cls(
            manifest_id=manifest_id,
            id=data.get("entity_id"),
            section=data.get("section"),
            name=data.get("name"),
            prompt=data.get("prompt"),
            critical=data.get("critical"),
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
            f"/manifest/{self.manifest_id}/check/{self.id}",
            "DELETE",
        )

    async def update(self, **kwargs):

        resp = await self.accqsure._query(
            f"/manifest/{self.manifest_id}/check/{self.id}",
            "PUT",
            None,
            dict(**kwargs),
        )
        exclude = ["id", "manifest_id", "accqsure"]

        for f in fields(self.__class__):
            if (
                f.name not in exclude and f.init and resp.get(f.name)
            ):  # Only update init args
                setattr(self, f.name, resp.get(f.name))
        return self

    async def refresh(self):

        resp = await self.accqsure._query(
            f"/manifest/{self.manifest_id}/check/{self.id}",
            "GET",
        )
        exclude = ["id", "manifest_id", "accqsure"]

        for f in fields(self.__class__):
            if (
                f.name not in exclude and f.init and resp.get(f.name)
            ):  # Only update init args
                setattr(self, f.name, resp.get(f.name))
        return self
