import json
import logging

from accqsure.exceptions import SpecificationError


class Inspections(object):
    def __init__(self, accqsure):
        self.accqsure = accqsure

    async def get(self, id, **kwargs):
        resp = await self.accqsure._query(f"/inspection/{id}", "GET", kwargs)
        return Inspection(self.accqsure, **resp)

    async def list(self, type, **kwargs):
        resp = await self.accqsure._query(
            f"/inspection",
            "GET",
            dict(type=type, **kwargs),
        )
        inspections = [
            Inspection(self.accqsure, **inspection) for inspection in resp
        ]
        return inspections

    async def create(
        self,
        type,
        name,
        document_type_id,
        manifests,
        draft=None,
        documents=None,
        **kwargs,
    ):

        data = dict(
            name=name,
            type=type,
            document_type_id=document_type_id,
            manifests=manifests,
            draft=draft,
            documents=documents**kwargs,
        )
        payload = {k: v for k, v in data.items() if v is not None}
        logging.info(f"Creating Inspection {name}")
        resp = await self.accqsure._query("/inspection", "POST", None, payload)
        inspection = Inspection(self.accqsure, **resp)
        logging.info(f"Created Inspection {name} with id {inspection.id}")

        return inspection

    async def remove(self, id, **kwargs):
        await self.accqsure._query(
            f"/inspection/{id}", "DELETE", dict(**kwargs)
        )


class Inspection:
    def __init__(self, accqsure, **kwargs):
        self.accqsure = accqsure
        self._entity = kwargs
        self._id = self._entity.get("entity_id")
        self._name = self._entity.get("name")
        self._status = self._entity.get("status")
        self._content_id = self._entity.get("doc_content_id")

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
        return f"Inspection( accqsure , **{self._entity.__repr__()})"

    def __bool__(self):
        return bool(self._id)

    async def remove(self):
        await self.accqsure._query(
            f"/inspection/{self._id}",
            "DELETE",
        )

    async def rename(self, name):
        resp = await self.accqsure._query(
            f"/inspection/{self._id}",
            "PUT",
            None,
            dict(name=name),
        )
        self.__init__(self.accqsure, **resp)
        return self

    async def refresh(self):
        resp = await self.accqsure._query(
            f"/inspection/{self.id}",
            "GET",
        )
        self.__init__(self.accqsure, **resp)
        return self

    async def get_contents(self):
        if not self._content_id:
            raise SpecificationError(
                "content_id", "Content not uploaded for inspection"
            )
        resp = await self.accqsure._query(
            f"/inspection/{self.id}/asset/{self._content_id}/manifest.json",
            "GET",
        )
        return resp

    async def get_content_item(self, name):
        if not self._content_id:
            raise SpecificationError(
                "content_id", "Content not uploaded for inspection"
            )
        return await self.accqsure._query(
            f"/inspection/{self.id}/asset/{self._content_id}/{name}",
            "GET",
        )
