from __future__ import annotations
from dataclasses import dataclass, field, fields
from typing import Optional, Any, TYPE_CHECKING, List
import logging

if TYPE_CHECKING:
    from accqsure import AccQsure


class DocumentTypes(object):
    """Manager for document type resources.

    Provides methods to create, retrieve, list, and delete document types.
    Document types define the schema and classification for documents.
    Maps to the /v1/document/type API endpoints.
    """

    def __init__(self, accqsure: "AccQsure") -> None:
        """Initialize the DocumentTypes manager.

        Args:
            accqsure: The AccQsure client instance.
        """
        self.accqsure = accqsure

    async def get(self, id_: str, **kwargs: Any) -> Optional["DocumentType"]:
        """Get a document type by ID.

        Retrieves a single document type by its entity ID.

        Args:
            id_: Document type entity ID (24-character string).
            **kwargs: Additional query parameters.

        Returns:
            DocumentType instance if found, None otherwise.

        Raises:
            ApiError: If the API returns an error.
            AccQsureException: If there's an error making the request.
        """
        resp = await self.accqsure._query(
            f"/document/type/{id_}", "GET", kwargs
        )
        return DocumentType.from_api(self.accqsure, resp)

    async def list(self, **kwargs: Any) -> List["DocumentType"]:
        """List all document types.

        Retrieves all document types available in the system.

        Args:
            **kwargs: Additional query parameters.

        Returns:
            List of DocumentType instances.

        Raises:
            ApiError: If the API returns an error.
            AccQsureException: If there's an error making the request.
        """
        resp = await self.accqsure._query("/document/type", "GET", kwargs)
        document_types = [
            DocumentType.from_api(self.accqsure, document_type)
            for document_type in resp
        ]
        return document_types

    async def create(
        self,
        name: str,
        code: str,
        level: int,
        **kwargs: Any,
    ) -> "DocumentType":
        """Create a new document type.

        Creates a new document type with the specified name, code, and level.
        Document types are used to classify and organize documents.

        Args:
            name: Name of the document type.
            code: Code identifier for the document type.
            level: Hierarchical level of the document type (integer).
            **kwargs: Additional document type properties.

        Returns:
            Created DocumentType instance.

        Raises:
            ApiError: If the API returns an error (e.g., validation error).
            AccQsureException: If there's an error making the request.
        """
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

    async def remove(self, id_: str, **kwargs: Any) -> None:
        """Delete a document type.

        Permanently deletes a document type by its entity ID.

        Args:
            id_: Document type entity ID (24-character string).
            **kwargs: Additional query parameters.

        Raises:
            ApiError: If the API returns an error (e.g., document type not found).
            AccQsureException: If there's an error making the request.
        """
        await self.accqsure._query(
            f"/document/type/{id_}", "DELETE", dict(**kwargs)
        )


@dataclass
class DocumentType:
    """Represents a document type in the AccQsure system.

    Document types define the classification and schema for documents.
    They are organized hierarchically by level and have a code identifier.
    """

    id: str
    name: str
    code: str
    level: int
    created_at: Optional[str] = field(default=None)
    updated_at: Optional[str] = field(default=None)

    @classmethod
    def from_api(
        cls, accqsure: "AccQsure", data: dict[str, Any]
    ) -> Optional["DocumentType"]:
        """Create a DocumentType instance from API response data.

        Args:
            accqsure: The AccQsure client instance.
            data: Dictionary containing document type data from the API.

        Returns:
            DocumentType instance if data is provided, None otherwise.
        """
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
        """Get the AccQsure client instance."""
        return self._accqsure

    @accqsure.setter
    def accqsure(self, value: "AccQsure") -> None:
        """Set the AccQsure client instance."""
        self._accqsure = value

    async def remove(self) -> None:
        """Delete this document type.

        Permanently deletes the document type from the system.

        Raises:
            ApiError: If the API returns an error.
            AccQsureException: If there's an error making the request.
        """
        await self.accqsure._query(
            f"/document/type/{self.id}",
            "DELETE",
        )

    async def update(self, **kwargs: Any) -> "DocumentType":
        """Update the document type.

        Updates document type properties and refreshes the instance with
        the latest data from the API.

        Args:
            **kwargs: Document type properties to update (e.g., name, code, level).

        Returns:
            Self for method chaining.

        Raises:
            ApiError: If the API returns an error.
            AccQsureException: If there's an error making the request.
        """
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

    async def refresh(self) -> "DocumentType":
        """Refresh the document type data from the API.

        Fetches the latest document type data from the API and updates the
        instance fields.

        Returns:
            Self for method chaining.

        Raises:
            ApiError: If the API returns an error.
            AccQsureException: If there's an error making the request.
        """
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
