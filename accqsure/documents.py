import json
import logging

from accqsure.exceptions import SpecificationError
from accqsure.manifests import Manifest


class Documents(object):
    def __init__(self, accqsure):
        self.accqsure = accqsure

    async def get(self, id, **kwargs):
        resp = await self.accqsure._query(f"/document/{id}", "GET", kwargs)
        return Document(self.accqsure, **resp)

    async def list(self, document_type_id, **kwargs):
        resp = await self.accqsure._query(
            f"/document", "GET", dict(document_type_id=document_type_id, **kwargs)
        )
        documents = [Document(self.accqsure, **document) for document in resp]
        return documents

    async def create(
        self,
        document_type_id,
        name,
        doc_id,
        **kwargs,
    ):

        data = dict(
            name=name,
            document_type_id=document_type_id,
            doc_id=doc_id,
            **kwargs,
        )
        payload = {k: v for k, v in data.items() if v is not None}
        logging.info(f"Creating Document {name}")
        resp = await self.accqsure._query("/document", "POST", None, payload)
        document = Document(self.accqsure, **resp)
        logging.info(f"Created Document {name} with id {document.id}")

        return document

    async def markdown_convert(self, title, type, base64_contents, **kwargs):
        resp = await self.accqsure._query(
            f"/document/convert",
            "POST",
            None,
            {**kwargs, **dict(title=title, type=type, base64_contents=base64_contents)},
        )
        return resp

    async def remove(self, id, **kwargs):
        await self.accqsure._query(f"/document/{id}", "DELETE", dict(**kwargs))


class Document:
    def __init__(self, accqsure, **kwargs):
        self.accqsure = accqsure
        self._entity = kwargs
        self._id = self._entity.get("entity_id")
        self._document_type_id = self._entity.get("document_type_id")
        self._name = self._entity.get("name")
        self._doc_id = self._entity.get("doc_id")
        self._content_id = self._entity.get("content_id")

    @property
    def id(self) -> str:
        return self._id

    @property
    def document_type_id(self) -> str:
        return self._document_type_id

    @property
    def name(self) -> str:
        return self._name

    @property
    def doc_id(self) -> str:
        return self._doc_id

    def __str__(self):
        return json.dumps({k: v for k, v in self._entity.items()})

    def __repr__(self):
        return f"Document( accqsure , **{self._entity.__repr__()})"

    def __bool__(self):
        return bool(self._id)

    async def remove(self):
        await self.accqsure._query(
            f"/document/{self._id}",
            "DELETE",
        )

    async def rename(self, name):
        resp = await self.accqsure._query(
            f"/document/{self._id}",
            "PUT",
            None,
            dict(name=name),
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

    async def get_contents(self):
        if not self._content_id:
            raise SpecificationError("content_id", "Content not uploaded for document")
        resp = await self.accqsure._query(
            f"/document/{self.id}/asset/{self._content_id}",
            "GET",
        )
        return resp

    async def set_contents(self, file_name, contents):
        resp = await self.accqsure._query(
            f"/document/{self.id}/asset/",
            "POST",
            dict(file_name=file_name),
            contents,
            {
                "Content-Type": "text/plain",
            },
        )
        asset_id = resp.get("asset_id")
        resp = await self.accqsure._query(
            f"/document/{self._id}",
            "PUT",
            None,
            dict(content_id=asset_id),
        )
        self.__init__(self.accqsure, **resp)
        return self

    async def list_manifests(self):
        resp = await self.accqsure._query(
            f"/document/{self.id}/manifest",
            "GET",
        )
        manifests = [Manifest(self.accqsure, **manifest) for manifest in resp]
        return manifests
