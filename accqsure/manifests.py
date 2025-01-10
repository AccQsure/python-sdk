import json
import logging

from accqsure.exceptions import SpecificationError


class Manifests(object):
    def __init__(self, accqsure):
        self.accqsure = accqsure

    async def get(self, id, **kwargs):
        resp = await self.accqsure._query(f"/manifest/{id}", "GET", kwargs)
        return Manifest(self.accqsure, **resp)

    async def get_global(self, **kwargs):
        resp = await self.accqsure._query(f"/manifest/global", "GET", kwargs)
        return Manifest(self.accqsure, **resp)

    async def list(self, document_type_id, **kwargs):
        resp = await self.accqsure._query(
            f"/manifest", "GET", dict(document_type_id=document_type_id, **kwargs)
        )
        manifests = [Manifest(self.accqsure, **manifest) for manifest in resp]
        return manifests

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
        logging.info(f"Creating Manifest {name}")
        resp = await self.accqsure._query("/manifest", "POST", None, payload)
        manifest = Manifest(self.accqsure, **resp)
        logging.info(f"Created Manifest {name} with id {manifest.id}")

        return manifest

    async def remove(self, id, **kwargs):
        await self.accqsure._query(f"/manifest/{id}", "DELETE", dict(**kwargs))


class Manifest:
    def __init__(self, accqsure, **kwargs):
        self.accqsure = accqsure
        self._entity = kwargs
        self._id = self._entity.get("entity_id")
        self._document_type_id = self._entity.get("document_type_id")
        self._name = self._entity.get("name")
        self._global = self._entity.get("global")
        self._reference_document = self._entity.get("reference_document")

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
    def reference_document_id(self) -> str:
        return self._reference_document.get("entity_id")

    @property
    def reference_document_doc_id(self) -> str:
        return self._reference_document.get("doc_id")

    def __str__(self):
        return json.dumps({k: v for k, v in self._entity.items()})

    def __repr__(self):
        return f"Manifest( accqsure , **{self._entity.__repr__()})"

    def __bool__(self):
        return bool(self._id)

    async def remove(self):
        await self.accqsure._query(
            f"/manifest/{self._id}",
            "DELETE",
        )

    async def rename(self, name):
        resp = await self.accqsure._query(
            f"/manifest/{self._id}",
            "PUT",
            None,
            dict(name=name),
        )
        self.__init__(self.accqsure, **resp)
        return self

    async def refresh(self):
        resp = await self.accqsure._query(
            f"/manifest/{self.id}",
            "GET",
        )
        self.__init__(self.accqsure, **resp)
        return self

    async def get_reference_contents(self):
        if not self._content_id:
            raise SpecificationError("content_id", "Content not uploaded for document")
        resp = await self.accqsure._query(
            f"/document/{self.id}/asset/{self._content_id}",
            "GET",
        )
        return resp

    async def list_checks(self, **kwargs):
        resp = await self.accqsure._query(f"/manifest/{self.id}/check", "GET", kwargs)
        checks = [ManifestCheck(self.accqsure, self, **check) for check in resp]
        return checks

    async def create_check(self, name, section, prompt, **kwargs):
        data = dict(
            name=name,
            section=section,
            prompt=prompt,
            **kwargs,
        )
        payload = {k: v for k, v in data.items() if v is not None}
        logging.info(f"Creating Manifest Check {name}")
        resp = await self.accqsure._query(
            f"/manifest/{self.id}/check", "POST", None, payload
        )
        check = ManifestCheck(self.accqsure, self, **resp)
        logging.info(f"Created Manifest Check {name} with id {check.id}")

        return check

    async def remove_check(self, check_id, **kwargs):
        await self.accqsure._query(
            f"/manifest/{self.id}/check/{check_id}", "DELETE", dict(**kwargs)
        )


class ManifestCheck:
    def __init__(self, accqsure, manifest, **kwargs):
        self.accqsure = accqsure
        self._entity = kwargs
        self._manifest = manifest
        self._id = self._entity.get("entity_id")
        self._section = self._entity.get("section")
        self._name = self._entity.get("name")
        self._prompt = self._entity.get("prompt")

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
    def prompt(self) -> str:
        return self._prompt

    def __str__(self):
        return json.dumps({k: v for k, v in self._entity.items()})

    def __repr__(self):
        return f"ManifestCheck( accqsure , **{self._entity.__repr__()})"

    def __bool__(self):
        return bool(self._id)

    async def remove(self):
        await self.accqsure._query(
            f"/manifest/{self._manifest.id}/check/{self.id}",
            "DELETE",
        )

    async def update(self, **kwargs):
        resp = await self.accqsure._query(
            f"/manifest/{self._manifest.id}/check/{self.id}",
            "PUT",
            None,
            dict(**kwargs),
        )
        self.__init__(self.accqsure, self._manifest, **resp)
        return self

    async def refresh(self):
        resp = await self.accqsure._query(
            f"/manifest/{self._manifest.id}/check/{self.id}",
            "GET",
        )
        self.__init__(self.accqsure, self._manifest, **resp)
        return self

    async def run(self, doc_content):
        reference_doc_content = await self._manifest.get_reference_contents()
        resp = await self.accqsure._query_stream(
            f"/manifest/{self._manifest.id}/check/{self.id}/run",
            "POST",
            None,
            dict(doc_content=doc_content, reference_doc_content=reference_doc_content),
        )
        return resp
