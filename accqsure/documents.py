from __future__ import annotations
from dataclasses import dataclass, field, fields
import logging
from typing import Optional, Any, TYPE_CHECKING, Dict, Tuple, List, Union

from accqsure.exceptions import SpecificationError
from accqsure.enums import MIME_TYPE
from accqsure.util import DocumentContents

if TYPE_CHECKING:
    from accqsure import AccQsure


class Documents:
    """Manager for document resources.

    Provides methods to create, retrieve, list, and delete documents.
    Maps to the /v1/document API endpoints.
    """

    def __init__(self, accqsure: "AccQsure") -> None:
        """Initialize the Documents manager.

        Args:
            accqsure: The AccQsure client instance.
        """
        self.accqsure = accqsure

    async def get(self, id_: str, **kwargs: Any) -> Optional["Document"]:
        """Get a document by ID.

        Retrieves a single document by its entity ID.

        Args:
            id_: Document entity ID (24-character string).
            **kwargs: Additional query parameters.

        Returns:
            Document instance if found, None otherwise.

        Raises:
            ApiError: If the API returns an error.
            AccQsureException: If there's an error making the request.
        """
        resp = await self.accqsure._query(f"/document/{id_}", "GET", kwargs)
        return Document.from_api(self.accqsure, resp)

    async def list(
        self, document_type_id: str, **kwargs: Any
    ) -> Tuple[List["Document"], Optional[str]]:
        """List documents filtered by document type.

        Retrieves a paginated list of documents for a specific document type.

        Args:
            document_type_id: Document type ID to filter by.
            **kwargs: Additional query parameters:
                - limit: Number of results to return (default: 50, max: 100).
                - start_key: Pagination cursor from previous response.

        Returns:
            Tuple of (list of Document instances, last_key for pagination).

        Raises:
            ApiError: If the API returns an error.
            AccQsureException: If there's an error making the request.
        """
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
        document_type_id: str,
        name: str,
        doc_id: str,
        contents: DocumentContents,
        **kwargs: Any,
    ) -> "Document":
        """Create a new document.

        Creates a new document with the specified type, name, document ID,
        and contents. The contents should be a DocumentContents dictionary
        (e.g., from Utilities.prepare_document_contents()).

        Args:
            document_type_id: Document type ID for the new document.
            name: Name of the document.
            doc_id: Document identifier (external ID).
            contents: DocumentContents dictionary containing document contents
                    (e.g., from Utilities.prepare_document_contents()).
            **kwargs: Additional document properties.

        Returns:
            Created Document instance.

        Raises:
            ApiError: If the API returns an error (e.g., validation error).
            AccQsureException: If there's an error making the request.
        """
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

    async def remove(self, id_: str, **kwargs: Any) -> None:
        """Delete a document.

        Permanently deletes a document by its entity ID.

        Args:
            id_: Document entity ID (24-character string).
            **kwargs: Additional query parameters.

        Raises:
            ApiError: If the API returns an error (e.g., document not found).
            AccQsureException: If there's an error making the request.
        """
        await self.accqsure._query(
            f"/document/{id_}", "DELETE", dict(**kwargs)
        )


@dataclass
class Document:
    """Represents a document in the AccQsure system.

    Documents are the data objects that contain original customer documents,
    records, and their associated metadata. Each document belongs to a document
    type and can have associated content assets.
    """

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
    ) -> Optional["Document"]:
        """Create a Document instance from API response data.

        Args:
            accqsure: The AccQsure client instance.
            data: Dictionary containing document data from the API.

        Returns:
            Document instance if data is provided, None otherwise.
        """
        if not data:
            return None
        entity = cls(
            id=data.get("entity_id"),
            name=data.get("name"),
            status=data.get("status"),
            document_type_id=data.get("document_type_id"),
            doc_id=data.get("doc_id"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
            content_id=data.get("content_id"),
        )
        entity.accqsure = accqsure
        return entity

    @property
    def accqsure(self) -> "AccQsure":
        return self._accqsure

    @accqsure.setter
    def accqsure(self, value: "AccQsure"):
        self._accqsure = value

    async def remove(self) -> None:
        """Delete this document.

        Permanently deletes the document from the system.

        Raises:
            ApiError: If the API returns an error.
            AccQsureException: If there's an error making the request.
        """
        await self.accqsure._query(
            f"/document/{self.id}",
            "DELETE",
        )

    async def rename(self, name: str) -> "Document":
        """Rename the document.

        Updates the document's name and refreshes the instance with the
        latest data from the API.

        Args:
            name: New name for the document.

        Returns:
            Self for method chaining.

        Raises:
            ApiError: If the API returns an error.
            AccQsureException: If there's an error making the request.
        """
        resp = await self.accqsure._query(
            f"/document/{self.id}",
            "PUT",
            None,
            dict(name=name),
        )
        exclude = ["id", "accqsure"]

        for f in fields(self.__class__):
            if (
                f.name not in exclude
                and f.init
                and resp.get(f.name) is not None
            ):  # Only update init args (skip derived like sections/waypoints)
                setattr(self, f.name, resp.get(f.name))
        return self

    async def refresh(self) -> "Document":
        """Refresh the document data from the API.

        Fetches the latest document data from the API and updates the
        instance fields.

        Returns:
            Self for method chaining.

        Raises:
            ApiError: If the API returns an error.
            AccQsureException: If there's an error making the request.
        """
        resp = await self.accqsure._query(
            f"/document/{self.id}",
            "GET",
        )
        exclude = ["id", "accqsure"]

        for f in fields(self.__class__):
            if (
                f.name not in exclude
                and f.init
                and resp.get(f.name) is not None
            ):  # Only update init args (skip derived like sections/waypoints)
                setattr(self, f.name, resp.get(f.name))
        return self

    async def get_contents(self) -> Dict[str, Any]:
        """Get the document content manifest.

        Retrieves the manifest.json file that describes the document's
        content assets.

        Returns:
            Dictionary containing the content manifest.

        Raises:
            SpecificationError: If content_id is not set (content not uploaded).
            ApiError: If the API returns an error.
            AccQsureException: If there's an error making the request.
        """
        if not self.content_id:
            raise SpecificationError(
                "content_id", "Content not uploaded for document"
            )

        resp = await self.accqsure._query(
            f"/document/{self.id}/asset/{self.content_id}/manifest.json",
            "GET",
        )
        return resp

    async def get_content_item(
        self, name: str
    ) -> Union[bytes, str, Dict[str, Any]]:
        """Get a specific content item from the document.

        Retrieves a named content item (file) from the document's assets.

        Args:
            name: Name of the content item to retrieve.

        Returns:
            Content item data (bytes, string, or dict depending on content type).

        Raises:
            SpecificationError: If content_id is not set (content not uploaded).
            ApiError: If the API returns an error.
            AccQsureException: If there's an error making the request.
        """
        if not self.content_id:
            raise SpecificationError(
                "content_id", "Content not uploaded for document"
            )

        return await self.accqsure._query(
            f"/document/{self.id}/asset/{self.content_id}/{name}",
            "GET",
        )

    async def _set_asset(
        self, path: str, file_name: str, mime_type: MIME_TYPE, contents: Any
    ) -> Any:
        """Set an asset file for the document (internal method).

        Args:
            path: Asset path within the document.
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
            f"/document/{self.id}/asset/{path}",
            "PUT",
            params={"file_name": file_name},
            data=contents,
            headers={"Content-Type": mime_type_str},
        )

    async def _set_content_item(
        self, name: str, file_name: str, mime_type: MIME_TYPE, contents: Any
    ) -> Any:
        """Set a content item for the document (internal method).

        Args:
            name: Name of the content item.
            file_name: Name of the file.
            mime_type: MIME type of the content (MIME_TYPE enum).
            contents: File contents (bytes, string, or file-like object).

        Returns:
            API response data.

        Raises:
            SpecificationError: If content_id is not set.
            ApiError: If the API returns an error.
        """
        if not self.content_id:
            raise SpecificationError(
                "content_id", "Content not finalized for inspection"
            )

        return await self._set_asset(
            f"{self.content_id}/{name}", file_name, mime_type, contents
        )
