import json
import logging


class DocumentTypes(object):
    def __init__(self, accqsure):
        self.accqsure = accqsure

    async def get(self, id, **kwargs):
        resp = await self.accqsure._query(f"/document/type/{id}", "GET", kwargs)
        return DocumentType(self.accqsure, **resp)

    async def list(self, **kwargs):
        resp = await self.accqsure._query(f"/document/type", "GET", kwargs)
        document_types = [
            DocumentType(self.accqsure, **document_type) for document_type in resp
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
        logging.info(f"Creating Document Type {name}")
        resp = await self.accqsure._query("/document/type", "POST", None, payload)
        document_type = DocumentType(self.accqsure, **resp)
        logging.info(f"Created Document Type {name} with id {document_type.id}")

        return document_type

    async def remove(self, id, **kwargs):
        await self.accqsure._query(f"/document/type/{id}", "DELETE", dict(**kwargs))


class DocumentType:
    def __init__(self, accqsure, **kwargs):
        self.accqsure = accqsure
        self._entity = kwargs
        self._id = self._entity.get("entity_id")
        self._name = self._entity.get("name")
        self._code = self._entity.get("code")
        self._level = self._entity.get("level")

    @property
    def id(self) -> str:
        return self._id

    @property
    def name(self) -> str:
        return self._name

    @property
    def code(self) -> str:
        return self._code

    @property
    def level(self) -> int:
        return self._level

    def __str__(self):
        return json.dumps({k: v for k, v in self._entity.items()})

    def __repr__(self):
        return f"DocumentType( accqsure , **{self._entity.__repr__()})"

    def __bool__(self):
        return bool(self._id)

    async def remove(self):
        await self.accqsure._query(
            f"/document/type/{self._id}",
            "DELETE",
        )

    async def update(self, **kwargs):
        resp = await self.accqsure._query(
            f"/document/type/{self._id}",
            "PUT",
            None,
            dict(**kwargs),
        )
        self.__init__(self.accqsure, **resp)
        return self

    async def refresh(self):
        resp = await self.accqsure._query(
            f"/document/{self.id}",
            "GET",
        )
        self.__init__(self.accqsure, **resp)
        return self
