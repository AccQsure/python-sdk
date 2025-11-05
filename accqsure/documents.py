from __future__ import annotations
from dataclasses import dataclass, field, fields
import logging
from typing import Optional, Any, TYPE_CHECKING

from accqsure.exceptions import SpecificationError

if TYPE_CHECKING:
    from accqsure import AccQsure


@dataclass
class Documents:
    accqsure: "AccQsure" = field(repr=False, compare=False, hash=False)

    async def get(self, id_, **kwargs):

        resp = await self.accqsure._query(f"/document/{id_}", "GET", kwargs)
        return Document.from_api(self.accqsure, resp)

    async def list(self, document_type_id, **kwargs):
        resp = await self.accqsure._query(
            "/document",
            "GET",
            dict(document_type_id=document_type_id, **kwargs),
        )

        documents = [
            Document.from_api(self.accqsure, document)
            for document in resp.get("results")
        ]
        return documents, resp.get("last_key")

    async def create(
        self,
        document_type_id,
        name,
        doc_id,
        contents,
        **kwargs,
    ):

        data = dict(
            name=name,
            document_type_id=document_type_id,
            doc_id=doc_id,
            contents=contents,
            **kwargs,
        )
        payload = {k: v for k, v in data.items() if v is not None}
        logging.info("Creating Document %s", name)

        resp = await self.accqsure._query("/document", "POST", None, payload)
        document = Document.from_api(self.accqsure, resp)
        logging.info("Created Document %s with id %s", name, document.id)

        return document

    async def remove(self, id_, **kwargs):

        await self.accqsure._query(
            f"/document/{id_}", "DELETE", dict(**kwargs)
        )


@dataclass
class Document:
    accqsure: "AccQsure" = field(repr=False, compare=False, hash=False)
    id: str
    name: str
    status: str
    doc_id: str
    created_at: str
    updated_at: str
    document_type_id: Optional[str] = field(default=None)
    content_id: Optional[str] = field(default=None)

    @classmethod
    def from_api(
        cls, accqsure: "AccQsure", data: dict[str, Any]
    ) -> "Document":
        if not data:
            return None
        return cls(
            accqsure=accqsure,
            id=data.get("entity_id"),
            name=data.get("name"),
            status=data.get("status"),
            document_type_id=data.get("document_type_id"),
            doc_id=data.get("doc_id"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
            content_id=data.get("content_id"),
        )

    async def remove(self):

        await self.accqsure._query(
            f"/document/{self.id}",
            "DELETE",
        )

    async def rename(self, name):

        resp = await self.accqsure._query(
            f"/document/{self.id}",
            "PUT",
            None,
            dict(name=name),
        )
        exclude = ["id", "accqsure"]

        for f in fields(self.__class__):
            if (
                f.name not in exclude and f.init and resp.get(f.name)
            ):  # Only update init args (skip derived like sections/waypoints)
                setattr(self, f.name, resp.get(f.name))
        return self

    async def refresh(self):

        resp = await self.accqsure._query(
            f"/document/{self.id}",
            "GET",
        )
        exclude = ["id", "accqsure"]

        for f in fields(self.__class__):
            if (
                f.name not in exclude and f.init and resp.get(f.name)
            ):  # Only update init args (skip derived like sections/waypoints)
                setattr(self, f.name, resp.get(f.name))
        return self

    async def get_contents(self):
        if not self.content_id:
            raise SpecificationError(
                "content_id", "Content not uploaded for document"
            )

        resp = await self.accqsure._query(
            f"/document/{self.id}/asset/{self.content_id}/manifest.json",
            "GET",
        )
        return resp

    async def get_content_item(self, name):
        if not self.content_id:
            raise SpecificationError(
                "content_id", "Content not uploaded for document"
            )

        return await self.accqsure._query(
            f"/document/{self.id}/asset/{self.content_id}/{name}",
            "GET",
        )

    async def _set_asset(self, path, file_name, mime_type, contents):
        return await self.accqsure._query(
            f"/document/{self.id}/asset/{path}",
            "PUT",
            params={"file_name": file_name},
            data=contents,
            headers={"Content-Type": mime_type},
        )

    async def _set_content_item(self, name, file_name, mime_type, contents):
        if not self.content_id:
            raise SpecificationError(
                "content_id", "Content not finalized for inspection"
            )

        return await self._set_asset(
            f"{self.content_id}/{name}", file_name, mime_type, contents
        )
