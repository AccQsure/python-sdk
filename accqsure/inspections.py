import json
import logging
from typing import Optional
from accqsure.exceptions import SpecificationError


class Inspections(object):
    def __init__(self, accqsure):

        self.accqsure = accqsure

    async def get(self, id_, **kwargs):

        resp = await self.accqsure._query(f"/inspection/{id_}", "GET", kwargs)
        return Inspection(self.accqsure, **resp)

    async def list(self, type_, limit=50, start_key=None, **kwargs):

        resp = await self.accqsure._query(
            "/inspection",
            "GET",
            {"type": type_, "limit": limit, "start_key": start_key, **kwargs},
        )
        inspections = [
            Inspection(self.accqsure, **inspection)
            for inspection in resp.get("results")
        ]
        return inspections, resp.get("last_key")

    async def create(
        self,
        type_,
        name,
        document_type_id,
        manifests,
        draft=None,
        documents=None,
        **kwargs,
    ):

        data = dict(
            name=name,
            type=type_,
            document_type_id=document_type_id,
            manifests=manifests,
            draft=draft,
            documents=documents**kwargs,
        )
        payload = {k: v for k, v in data.items() if v is not None}
        logging.info("Creating Inspection %s", name)

        resp = await self.accqsure._query("/inspection", "POST", None, payload)
        inspection = Inspection(self.accqsure, **resp)
        logging.info("Created Inspection %s with id %s", name, inspection.id)

        return inspection

    async def remove(self, id_, **kwargs):

        await self.accqsure._query(f"/inspection/{id_}", "DELETE", {**kwargs})


class Inspection:
    def __init__(self, accqsure, **kwargs):
        self.accqsure = accqsure
        self._entity = kwargs
        self._id = self._entity.get("entity_id")
        self._name = self._entity.get("name")
        self._type = self._entity.get("type")
        self._status = self._entity.get("status")
        self._doc_content_id = self._entity.get("doc_content_id")
        self._content_id = self._entity.get("content_id")

    @property
    def id(self) -> str:
        return self._id

    @property
    def type(self) -> str:
        return self._type

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

    async def get_doc_contents(self):
        if not self._doc_content_id:
            raise SpecificationError(
                "doc_content_id",
                "Document content not uploaded for inspection",
            )

        resp = await self.accqsure._query(
            f"/inspection/{self.id}/asset/{self._doc_content_id}/manifest.json",
            "GET",
        )
        return resp

    async def get_doc_content_item(self, name):
        if not self._doc_content_id:
            raise SpecificationError(
                "doc_content_id", "Document not uploaded for inspection"
            )

        return await self.accqsure._query(
            f"/inspection/{self.id}/asset/{self._doc_content_id}/{name}",
            "GET",
        )

    async def _set_doc_content_item(
        self, name, file_name, mime_type, contents
    ):
        if not self._doc_content_id:
            raise SpecificationError(
                "content_id", "Content not finalized for inspection"
            )

        return await self.accqsure._query(
            f"/inspection/{self.id}/asset/{self._doc_content_id}/{name}",
            "PUT",
            params={"file_name": file_name},
            data=contents,
            headers={"Content-Type": mime_type},
        )

    async def get_contents(self):
        if not self._content_id:
            raise SpecificationError(
                "content_id", "Content not finalized for inspection"
            )

        resp = await self.accqsure._query(
            f"/inspection/{self.id}/asset/{self._content_id}/manifest.json",
            "GET",
        )
        return resp

    async def get_content_item(self, name):
        if not self._content_id:
            raise SpecificationError(
                "content_id", "Content not finalized for inspection"
            )

        return await self.accqsure._query(
            f"/inspection/{self.id}/asset/{self._content_id}/{name}",
            "GET",
        )

    async def _set_content_item(self, name, file_name, mime_type, contents):
        if not self._content_id:
            raise SpecificationError(
                "content_id", "Content not finalized for inspection"
            )

        return await self.accqsure._query(
            f"/inspection/{self.id}/asset/{self._content_id}/{name}",
            "PUT",
            params={"file_name": file_name},
            data=contents,
            headers={"Content-Type": mime_type},
        )

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
            InspectionCheck(self.accqsure, self, **check)
            for check in resp.get("results")
        ]
        return checks, resp.get("last_key")


class InspectionCheck:
    def __init__(self, accqsure, inspection, **kwargs):
        self.accqsure = accqsure
        self._entity = kwargs
        self._inspection = inspection
        self._id = self._entity.get("entity_id")
        self._section = self._entity.get("check_section")
        self._name = self._entity.get("check_name")
        self._status = self._entity.get("status")
        self._critical = self._entity.get("critical")
        self._compliant = self._entity.get("compliant")
        self._rationale = self._entity.get("rationale")
        self._suggestion = self._entity.get("suggestion")

    @property
    def id(self) -> str:
        return self._id

    @property
    def section(self) -> str:
        return self._section

    @property
    def name(self) -> str:
        return self._name

    @property
    def status(self) -> str:
        return self._status

    @property
    def critical(self) -> bool:
        return self._critical

    @property
    def compliant(self) -> Optional[bool]:
        return self._compliant

    @property
    def rationale(self) -> Optional[str]:
        return self._rationale

    @property
    def suggestion(self) -> Optional[str]:
        return self._suggestion

    def __str__(self):
        return json.dumps({k: v for k, v in self._entity.items()})

    def __repr__(self):
        return f"InspectionCheck( accqsure , **{self._entity.__repr__()})"

    def __bool__(self):
        return bool(self._id)

    async def update(self, **kwargs):

        resp = await self.accqsure._query(
            f"/inspection/{self._inspection.id}/check/{self.id}",
            "PUT",
            None,
            dict(**kwargs),
        )
        self.__init__(self.accqsure, self._inspection, **resp)
        return self

    async def refresh(self):

        resp = await self.accqsure._query(
            f"/inspection/{self._inspection.id}/check/{self.id}",
            "GET",
        )
        self.__init__(self.accqsure, self._inspection, **resp)
        return self
