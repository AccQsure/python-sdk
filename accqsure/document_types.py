from __future__ import annotations
from dataclasses import dataclass, field, fields
from typing import Optional, Any, TYPE_CHECKING
import logging

if TYPE_CHECKING:
    from accqsure import AccQsure


class DocumentTypes(object):
    def __init__(self, accqsure):
        self.accqsure = accqsure

    async def get(self, id_, **kwargs):
        resp = await self.accqsure._query(
            f"/document/type/{id_}", "GET", kwargs
        )
        return DocumentType.from_api(self.accqsure, resp)

    async def list(self, **kwargs):
        resp = await self.accqsure._query("/document/type", "GET", kwargs)
        document_types = [
            DocumentType.from_api(self.accqsure, document_type)
            for document_type in resp
        ]
        return document_types

    async def create(
        self,
        name,
        code,
        level,
        **kwargs,
    ):

        data = dict(
            name=name,
            code=code,
            level=level,
            **kwargs,
        )
        payload = {k: v for k, v in data.items() if v is not None}
        logging.info("Creating Document Type %s", name)
        resp = await self.accqsure._query(
            "/document/type", "POST", None, payload
        )
        document_type = DocumentType.from_api(self.accqsure, resp)
        logging.info(
            "Created Document Type %s with id %s", name, document_type.id
        )

        return document_type

    async def remove(self, id_, **kwargs):
        await self.accqsure._query(
            f"/document/type/{id_}", "DELETE", dict(**kwargs)
        )


@dataclass
class DocumentType:
    id: str
    name: str
    code: str
    level: int
    created_at: Optional[str] = field(default=None)
    updated_at: Optional[str] = field(default=None)

    @classmethod
    def from_api(
        cls, accqsure: "AccQsure", data: dict[str, Any]
    ) -> "DocumentType":
        if not data:
            return None
        entity = cls(
            id=data.get("entity_id"),
            name=data.get("name"),
            code=data.get("code"),
            level=data.get("level"),
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
            f"/document/type/{self.id}",
            "DELETE",
        )

    async def update(self, **kwargs):
        resp = await self.accqsure._query(
            f"/document/type/{self.id}",
            "PUT",
            None,
            dict(**kwargs),
        )
        exclude = ["id", "accqsure"]

        for f in fields(self.__class__):
            if (
                f.name not in exclude
                and f.init
                and resp.get(f.name) is not None
            ):  # Only update init args
                setattr(self, f.name, resp.get(f.name))
        return self

    async def refresh(self):
        resp = await self.accqsure._query(
            f"/document/type/{self.id}",
            "GET",
        )
        exclude = ["id", "accqsure"]

        for f in fields(self.__class__):
            if (
                f.name not in exclude
                and f.init
                and resp.get(f.name) is not None
            ):  # Only update init args
                setattr(self, f.name, resp.get(f.name))
        return self
