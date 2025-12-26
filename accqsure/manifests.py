from __future__ import annotations
from dataclasses import dataclass, field, fields
from typing import Optional, Any, TYPE_CHECKING, List, Tuple, Union, Dict
import logging

from accqsure.exceptions import SpecificationError
from accqsure.documents import Document
from accqsure.enums import MIME_TYPE

if TYPE_CHECKING:
    from accqsure import AccQsure


class Manifests(object):
    """Manager for manifest resources.

    Provides methods to create, retrieve, list, and delete manifests.
    Manifests define validation checks that are used in inspections.
    Maps to the /v1/manifest API endpoints.
    """

    def __init__(self, accqsure: "AccQsure") -> None:
        """Initialize the Manifests manager.

        Args:
            accqsure: The AccQsure client instance.
        """
        self.accqsure = accqsure

    async def get(self, id_: str, **kwargs: Any) -> Optional["Manifest"]:
        """Get a manifest by ID.

        Retrieves a single manifest by its entity ID.

        Args:
            id_: Manifest entity ID (24-character string).
            **kwargs: Additional query parameters.

        Returns:
            Manifest instance if found, None otherwise.

        Raises:
            ApiError: If the API returns an error.
            AccQsureException: If there's an error making the request.
        """
        resp = await self.accqsure._query(f"/manifest/{id_}", "GET", kwargs)
        return Manifest.from_api(self.accqsure, resp)

    async def get_global(self, **kwargs: Any) -> Optional["Manifest"]:
        """Get the global manifest.

        Retrieves the global manifest for the organization.

        Args:
            **kwargs: Additional query parameters.

        Returns:
            Manifest instance if found, None otherwise.

        Raises:
            ApiError: If the API returns an error.
            AccQsureException: If there's an error making the request.
        """
        resp = await self.accqsure._query("/manifest/global", "GET", kwargs)
        return Manifest.from_api(self.accqsure, resp)

    async def list(
        self,
        document_type_id: str,
        limit: int = 50,
        start_key: Optional[str] = None,
        fetch_all: bool = False,
        **kwargs: Any,
    ) -> Union[List["Manifest"], Tuple[List["Manifest"], Optional[str]]]:
        """List manifests filtered by document type.

        Retrieves a list of manifests for a specific document type.
        Can return all results or paginated results.

        Args:
            document_type_id: Document type ID to filter by.
            limit: Number of results to return per page (default: 50, max: 100).
                   Only used if fetch_all is False.
            start_key: Pagination cursor from previous response.
                      Only used if fetch_all is False.
            fetch_all: If True, fetches all results across all pages.
                      If False, returns paginated results.
            **kwargs: Additional query parameters.

        Returns:
            If fetch_all is True: List of all Manifest instances.
            If fetch_all is False: Tuple of (list of Manifest instances,
                                          last_key for pagination).

        Raises:
            ApiError: If the API returns an error.
            AccQsureException: If there's an error making the request.
        """
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
        document_type_id: str,
        name: str,
        reference_document_id: Optional[str],
        **kwargs: Any,
    ) -> "Manifest":
        """Create a new manifest.

        Creates a new manifest with the specified document type, name, and
        reference document. Manifests define validation checks that are
        used in inspections.

        Args:
            document_type_id: Document type ID for the manifest.
            name: Name of the manifest.
            reference_document_id: Reference document ID to use as a template.
            **kwargs: Additional manifest properties.

        Returns:
            Created Manifest instance.

        Raises:
            ApiError: If the API returns an error (e.g., validation error).
            AccQsureException: If there's an error making the request.
        """
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

    async def remove(self, id_: str, **kwargs: Any) -> None:
        """Delete a manifest.

        Permanently deletes a manifest by its entity ID.

        Args:
            id_: Manifest entity ID (24-character string).
            **kwargs: Additional query parameters.

        Raises:
            ApiError: If the API returns an error (e.g., manifest not found).
            AccQsureException: If there's an error making the request.
        """
        await self.accqsure._query(
            f"/manifest/{id_}", "DELETE", dict(**kwargs)
        )


@dataclass
class Manifest:
    """Represents a manifest in the AccQsure system.

    Manifests define validation checks that are used in inspections to
    validate documents. They can have a reference document that serves
    as a template or example.
    """

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
    ) -> Optional["Manifest"]:
        """Create a Manifest instance from API response data.

        Args:
            accqsure: The AccQsure client instance.
            data: Dictionary containing manifest data from the API.

        Returns:
            Manifest instance if data is provided, None otherwise.
        """
        if not data:
            return None
        entity = cls(
            id=data.get("entity_id"),
            name=data.get("name"),
            document_type_id=data.get("document_type_id"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
            global_=data.get("global"),
            reference_document=(
                Document.from_api(
                    accqsure=accqsure, data=data.get("reference_document")
                )
                if data.get("reference_document")
                else None
            ),
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
        """Get the reference document entity ID.

        Returns:
            Reference document entity ID, or "UNKNOWN" if not set.
        """
        return (
            self.reference_document.id
            if self.reference_document
            else "UNKNOWN"
        )

    @property
    def reference_document_doc_id(self) -> str:
        """Get the reference document doc_id.

        Returns:
            Reference document doc_id, or "UNKNOWN" if not set.
        """
        return (
            self.reference_document.doc_id
            if self.reference_document
            else "UNKNOWN"
        )

    async def remove(self) -> None:
        """Delete this manifest.

        Permanently deletes the manifest from the system.

        Raises:
            ApiError: If the API returns an error.
            AccQsureException: If there's an error making the request.
        """
        await self.accqsure._query(
            f"/manifest/{self.id}",
            "DELETE",
        )

    async def rename(self, name: str) -> "Manifest":
        """Rename the manifest.

        Updates the manifest's name and refreshes the instance with the
        latest data from the API.

        Args:
            name: New name for the manifest.

        Returns:
            Self for method chaining.

        Raises:
            ApiError: If the API returns an error.
            AccQsureException: If there's an error making the request.
        """
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

    async def refresh(self) -> "Manifest":
        """Refresh the manifest data from the API.

        Fetches the latest manifest data from the API and updates the
        instance fields, including the reference document if present.

        Returns:
            Self for method chaining.

        Raises:
            ApiError: If the API returns an error.
            AccQsureException: If there's an error making the request.
        """
        resp = await self.accqsure._query(
            f"/manifest/{self.id}",
            "GET",
        )
        exclude = ["id", "accqsure", "reference_document"]

        for f in fields(self.__class__):
            if (
                f.name not in exclude
                and f.init
                and resp.get(f.name) is not None
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

    async def get_reference_contents(self) -> Dict[str, Any]:
        """Get the reference document content manifest.

        Retrieves the manifest.json file that describes the reference
        document's content assets.

        Returns:
            Dictionary containing the content manifest.

        Raises:
            SpecificationError: If reference_document or content_id is not set.
            ApiError: If the API returns an error.
            AccQsureException: If there's an error making the request.
        """
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

    async def get_reference_content_item(
        self, name: str
    ) -> Union[bytes, str, Dict[str, Any]]:
        """Get a specific content item from the reference document.

        Retrieves a named content item (file) from the reference document's
        assets.

        Args:
            name: Name of the content item to retrieve.

        Returns:
            Content item data (bytes, string, or dict depending on content type).

        Raises:
            SpecificationError: If reference_document or content_id is not set.
            ApiError: If the API returns an error.
            AccQsureException: If there's an error making the request.
        """
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

    async def list_checks(
        self,
        limit: int = 50,
        start_key: Optional[str] = None,
        **kwargs: Any,
    ) -> Tuple[List["ManifestCheck"], Optional[str]]:
        """List manifest checks.

        Retrieves a paginated list of checks defined in this manifest.

        Args:
            limit: Number of results to return (default: 50, max: 100).
            start_key: Pagination cursor from previous response.
            **kwargs: Additional query parameters.

        Returns:
            Tuple of (list of ManifestCheck instances, last_key for pagination).

        Raises:
            ApiError: If the API returns an error.
            AccQsureException: If there's an error making the request.
        """
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

    async def create_check(
        self, name: str, section: str, prompt: str, **kwargs: Any
    ) -> "ManifestCheck":
        """Create a new manifest check.

        Creates a new validation check in this manifest. Checks define
        the validation rules that are applied during inspections.

        Args:
            name: Name of the check.
            section: Section name where the check belongs.
            prompt: Validation prompt or description for the check.
            **kwargs: Additional check properties (e.g., critical flag).

        Returns:
            Created ManifestCheck instance.

        Raises:
            ApiError: If the API returns an error (e.g., validation error).
            AccQsureException: If there's an error making the request.
        """
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

    async def remove_check(self, check_id: str, **kwargs: Any) -> None:
        """Delete a manifest check.

        Permanently deletes a check from this manifest.

        Args:
            check_id: Manifest check entity ID (24-character string).
            **kwargs: Additional query parameters.

        Raises:
            ApiError: If the API returns an error (e.g., check not found).
            AccQsureException: If there's an error making the request.
        """
        await self.accqsure._query(
            f"/manifest/{self.id}/check/{check_id}", "DELETE", dict(**kwargs)
        )

    async def _set_asset(
        self, path: str, file_name: str, mime_type: MIME_TYPE, contents: Any
    ) -> Any:
        """Set an asset file for the manifest (internal method).

        Args:
            path: Asset path within the manifest.
            file_name: Name of the file.
            mime_type: MIME type of the content (MIME_TYPE enum).
            contents: File contents (bytes, string, or file-like object).

        Returns:
            API response data.

        Raises:
            ApiError: If the API returns an error.
        """
        mime_type_str = (
            mime_type.value if isinstance(mime_type, MIME_TYPE) else mime_type
        )
        return await self.accqsure._query(
            f"/manifest/{self.id}/asset/{path}",
            "PUT",
            params={"file_name": file_name},
            data=contents,
            headers={"Content-Type": mime_type_str},
        )


@dataclass
class ManifestCheck:
    """Represents a manifest check (validation rule) in the AccQsure system.

    Manifest checks define validation rules that are applied during
    inspections. Each check has a name, section, prompt, and optional
    critical flag.
    """

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
    ) -> Optional["ManifestCheck"]:
        """Create a ManifestCheck instance from API response data.

        Args:
            accqsure: The AccQsure client instance.
            manifest_id: The manifest ID this check belongs to.
            data: Dictionary containing manifest check data from the API.

        Returns:
            ManifestCheck instance if data is provided, None otherwise.
        """
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
        """Get the AccQsure client instance."""
        return self._accqsure

    @accqsure.setter
    def accqsure(self, value: "AccQsure") -> None:
        """Set the AccQsure client instance."""
        self._accqsure = value

    async def remove(self) -> None:
        """Delete this manifest check.

        Permanently deletes the check from the manifest.

        Raises:
            ApiError: If the API returns an error.
            AccQsureException: If there's an error making the request.
        """
        await self.accqsure._query(
            f"/manifest/{self.manifest_id}/check/{self.id}",
            "DELETE",
        )

    async def update(self, **kwargs: Any) -> "ManifestCheck":
        """Update the manifest check.

        Updates manifest check properties (e.g., name, section, prompt,
        critical flag) and refreshes the instance with the latest data
        from the API.

        Args:
            **kwargs: Manifest check properties to update.

        Returns:
            Self for method chaining.

        Raises:
            ApiError: If the API returns an error.
            AccQsureException: If there's an error making the request.
        """
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

    async def refresh(self) -> "ManifestCheck":
        """Refresh the manifest check data from the API.

        Fetches the latest manifest check data from the API and updates the
        instance fields.

        Returns:
            Self for method chaining.

        Raises:
            ApiError: If the API returns an error.
            AccQsureException: If there's an error making the request.
        """
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
