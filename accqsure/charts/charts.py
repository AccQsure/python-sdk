import json
import logging
from accqsure.exceptions import SpecificationError
from .sections import ChartSections
from .waypoints import ChartWaypoints


class Charts(object):
    def __init__(self, accqsure):
        self.accqsure = accqsure

    async def get(self, id_, **kwargs):

        resp = await self.accqsure._query(f"/chart/{id_}", "GET", kwargs)
        return Chart(self.accqsure, **resp)

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
                Chart(self.accqsure, **chart) for chart in resp.get("results")
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
                Chart(self.accqsure, **chart) for chart in resp.get("results")
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
        chart = Chart(self.accqsure, **resp)
        logging.info("Created Chart %s with id %s", name, chart.id)

        return chart

    async def remove(self, id_, **kwargs):

        await self.accqsure._query(f"/chart/{id_}", "DELETE", {**kwargs})


class Chart:
    def __init__(self, accqsure, **kwargs):
        self.accqsure = accqsure
        self._entity = kwargs
        self._id = self._entity.get("entity_id")
        self._name = self._entity.get("name")
        self._document_type_id = self._entity.get("document_type_id")
        self._status = self._entity.get("status")
        self._reference_document = self._entity.get("reference_document")
        self.sections = ChartSections(self.accqsure, self._id)
        self.waypoints = ChartWaypoints(self.accqsure, self._id)

    @property
    def id(self) -> str:
        return self._id

    @property
    def document_type_id(self) -> str:
        return self._document_type_id

    @property
    def status(self) -> str:
        return self._status

    @property
    def name(self) -> str:
        return self._name

    @property
    def reference_document_id(self) -> str:

        return (
            self._reference_document.get("entity_id")
            if self._reference_document
            else "UNKNOWN"
        )

    @property
    def reference_document_doc_id(self) -> str:
        return (
            self._reference_document.get("doc_id")
            if self._reference_document
            else "UNKNOWN"
        )

    def __str__(self):
        return json.dumps({k: v for k, v in self._entity.items()})

    def __repr__(self):
        return f"Chart( accqsure , **{self._entity.__repr__()})"

    def __bool__(self):
        return bool(self._id)

    async def remove(self):

        await self.accqsure._query(
            f"/chart/{self._id}",
            "DELETE",
        )

    async def rename(self, name):

        resp = await self.accqsure._query(
            f"/chart/{self._id}",
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
        self.__init__(self.accqsure, **resp)
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
        if not self._reference_document:
            raise SpecificationError(
                "reference_document",
                "Reference document not found for manifest",
            )
        document_id = self._reference_document.get("entity_id")
        content_id = self._reference_document.get("content_id")
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
        if not self._reference_document:
            raise SpecificationError(
                "reference_document",
                "Reference document not found for manifest",
            )
        document_id = self._reference_document.get("entity_id")
        content_id = self._reference_document.get("content_id")
        if not content_id:
            raise SpecificationError(
                "content_id", "Content not uploaded for document"
            )
        resp = await self.accqsure._query(
            f"/document/{document_id}/asset/{content_id}/{name}",
            "GET",
        )
        return resp
