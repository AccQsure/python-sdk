from __future__ import annotations
from dataclasses import dataclass, field, fields
from typing import Optional, Any, TYPE_CHECKING, List, Tuple, Dict, Union
import logging

from accqsure.exceptions import SpecificationError
from accqsure.enums import INSPECTION_TYPE, MIME_TYPE
from accqsure.util import DocumentContents

if TYPE_CHECKING:
    from accqsure import AccQsure


class Inspections(object):
    """Manager for inspection resources.

    Provides methods to create, retrieve, list, and delete inspections.
    Inspections are used to validate documents against manifest checks.
    Maps to the /v1/inspection API endpoints.
    """

    def __init__(self, accqsure: "AccQsure") -> None:
        """Initialize the Inspections manager.

        Args:
            accqsure: The AccQsure client instance.
        """
        self.accqsure = accqsure

    async def get(self, id_: str, **kwargs: Any) -> Optional["Inspection"]:
        """Get an inspection by ID.

        Retrieves a single inspection by its entity ID.

        Args:
            id_: Inspection entity ID (24-character string).
            **kwargs: Additional query parameters.

        Returns:
            Inspection instance if found, None otherwise.

        Raises:
            ApiError: If the API returns an error.
            AccQsureException: If there's an error making the request.
        """
        resp = await self.accqsure._query(f"/inspection/{id_}", "GET", kwargs)
        return Inspection.from_api(self.accqsure, resp)

    async def list(
        self,
        inspection_type: INSPECTION_TYPE,
        limit: int = 50,
        start_key: Optional[str] = None,
        **kwargs: Any,
    ) -> Tuple[List["Inspection"], Optional[str]]:
        """List inspections filtered by type.

        Retrieves a paginated list of inspections for a specific inspection type.

        Args:
            inspection_type: Inspection type to filter by (INSPECTION_TYPE enum).
            limit: Number of results to return (default: 50, max: 100).
            start_key: Pagination cursor from previous response.
            **kwargs: Additional query parameters.

        Returns:
            Tuple of (list of Inspection instances, last_key for pagination).

        Raises:
            ApiError: If the API returns an error.
            AccQsureException: If there's an error making the request.
        """
        resp = await self.accqsure._query(
            "/inspection",
            "GET",
            {
                "type": (
                    inspection_type.value
                    if isinstance(inspection_type, INSPECTION_TYPE)
                    else inspection_type
                ),
                "limit": limit,
                "start_key": start_key,
                **kwargs,
            },
        )
        inspections = [
            Inspection.from_api(self.accqsure, inspection)
            for inspection in resp.get("results")
        ]
        return inspections, resp.get("last_key")

    async def create(
        self,
        inspection_type: INSPECTION_TYPE,
        name: str,
        document_type_id: str,
        manifests: List[str],
        draft: Optional[DocumentContents] = None,
        documents: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> "Inspection":
        """Create a new inspection.

        Creates a new inspection with the specified type, name, document type,
        and associated manifests. Inspections validate documents against
        manifest checks.

        Args:
            inspection_type: Type of inspection to create (INSPECTION_TYPE enum).
            name: Name of the inspection.
            document_type_id: Document type ID for the inspection.
            manifests: List of manifest IDs to use for validation.
            draft: DocumentContents dictionary for the draft document
                   (for preliminary inspections only, e.g., from
                   Utilities.prepare_document_contents()).
            documents: List of document IDs to inspect (for effective inspections only).
            **kwargs: Additional inspection properties.

        Returns:
            Created Inspection instance.

        Raises:
            ApiError: If the API returns an error (e.g., validation error).
            AccQsureException: If there's an error making the request.
        """
        data = dict(
            name=name,
            type=(
                inspection_type.value
                if isinstance(inspection_type, INSPECTION_TYPE)
                else inspection_type
            ),
            document_type_id=document_type_id,
            manifests=manifests,
            draft=draft,
            documents=documents,
            **kwargs,
        )
        payload = {k: v for k, v in data.items() if v is not None}
        logging.info("Creating Inspection %s", name)

        resp = await self.accqsure._query("/inspection", "POST", None, payload)
        inspection = Inspection.from_api(self.accqsure, resp)
        logging.info("Created Inspection %s with id %s", name, inspection.id)

        return inspection

    async def remove(self, id_: str, **kwargs: Any) -> None:
        """Delete an inspection.

        Permanently deletes an inspection by its entity ID.

        Args:
            id_: Inspection entity ID (24-character string).
            **kwargs: Additional query parameters.

        Raises:
            ApiError: If the API returns an error (e.g., inspection not found).
            AccQsureException: If there's an error making the request.
        """
        await self.accqsure._query(f"/inspection/{id_}", "DELETE", {**kwargs})


@dataclass
class Inspection:
    """Represents an inspection in the AccQsure system.

    Inspections validate documents against manifest checks. They can be
    run to generate inspection reports with compliance results.

    Attributes:
        id: Entity ID of the inspection.
        name: Name of the inspection.
        type: Inspection type (should be one of INSPECTION_TYPE enum values:
              'preliminary' or 'effective').
        status: Current status of the inspection.
    """

    id: str
    name: str
    type: str  # Should be one of INSPECTION_TYPE enum values
    status: str
    created_at: Optional[str] = field(default=None)
    updated_at: Optional[str] = field(default=None)
    document_type_id: Optional[str] = field(default=None)
    doc_content_id: Optional[str] = field(default=None)
    content_id: Optional[str] = field(default=None)

    @classmethod
    def from_api(
        cls, accqsure: "AccQsure", data: dict[str, Any]
    ) -> Optional["Inspection"]:
        """Create an Inspection instance from API response data.

        Args:
            accqsure: The AccQsure client instance.
            data: Dictionary containing inspection data from the API.

        Returns:
            Inspection instance if data is provided, None otherwise.
        """
        if not data:
            return None
        entity = cls(
            id=data.get("entity_id"),
            name=data.get("name"),
            type=data.get("type"),
            status=data.get("status"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
            document_type_id=data.get("document_type_id"),
            doc_content_id=data.get("doc_content_id"),
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
        """Delete this inspection.

        Permanently deletes the inspection from the system.

        Raises:
            ApiError: If the API returns an error.
            AccQsureException: If there's an error making the request.
        """
        await self.accqsure._query(
            f"/inspection/{self.id}",
            "DELETE",
        )

    async def rename(self, name: str) -> "Inspection":
        """Rename the inspection.

        Updates the inspection's name and refreshes the instance with the
        latest data from the API.

        Args:
            name: New name for the inspection.

        Returns:
            Self for method chaining.

        Raises:
            ApiError: If the API returns an error.
            AccQsureException: If there's an error making the request.
        """
        resp = await self.accqsure._query(
            f"/inspection/{self.id}",
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
            ):  # Only update init args
                setattr(self, f.name, resp.get(f.name))
        return self

    async def run(self) -> "Inspection":
        """Run the inspection.

        Executes the inspection, validating documents against manifest checks
        and generating inspection results. This is an asynchronous operation
        that may take time to complete.

        Returns:
            Self for method chaining.

        Raises:
            ApiError: If the API returns an error.
            AccQsureException: If there's an error making the request.
        """
        resp = await self.accqsure._query(
            f"/inspection/{self.id}/run",
            "POST",
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

    async def refresh(self) -> "Inspection":
        """Refresh the inspection data from the API.

        Fetches the latest inspection data from the API and updates the
        instance fields.

        Returns:
            Self for method chaining.

        Raises:
            ApiError: If the API returns an error.
            AccQsureException: If there's an error making the request.
        """
        resp = await self.accqsure._query(
            f"/inspection/{self.id}",
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

    async def _set_asset(
        self, path: str, file_name: str, mime_type: MIME_TYPE, contents: Any
    ) -> Any:
        """Set an asset file for the inspection (internal method).

        Args:
            path: Asset path within the inspection.
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
            f"/inspection/{self.id}/asset/{path}",
            "PUT",
            params={"file_name": file_name},
            data=contents,
            headers={"Content-Type": mime_type_str},
        )

    async def get_doc_contents(self) -> Dict[str, Any]:
        """Get the document content manifest for the inspection.

        Retrieves the manifest.json file that describes the document content
        assets uploaded for this inspection.

        Returns:
            Dictionary containing the document content manifest.

        Raises:
            SpecificationError: If doc_content_id is not set.
            ApiError: If the API returns an error.
            AccQsureException: If there's an error making the request.
        """
        if not self.doc_content_id:
            raise SpecificationError(
                "doc_content_id",
                "Document content not uploaded for inspection",
            )

        resp = await self.accqsure._query(
            f"/inspection/{self.id}/asset/{self.doc_content_id}/manifest.json",
            "GET",
        )
        return resp

    async def get_doc_content_item(
        self, name: str
    ) -> Union[bytes, str, Dict[str, Any]]:
        """Get a specific document content item from the inspection.

        Retrieves a named content item (file) from the inspection's document
        content assets.

        Args:
            name: Name of the content item to retrieve.

        Returns:
            Content item data (bytes, string, or dict depending on content type).

        Raises:
            SpecificationError: If doc_content_id is not set.
            ApiError: If the API returns an error.
            AccQsureException: If there's an error making the request.
        """
        if not self.doc_content_id:
            raise SpecificationError(
                "doc_content_id", "Document not uploaded for inspection"
            )

        return await self.accqsure._query(
            f"/inspection/{self.id}/asset/{self.doc_content_id}/{name}",
            "GET",
        )

    async def _set_doc_content_item(
        self, name: str, file_name: str, mime_type: MIME_TYPE, contents: Any
    ) -> Any:
        """Set a document content item for the inspection (internal method).

        Args:
            name: Name of the content item.
            file_name: Name of the file.
            mime_type: MIME type of the content (MIME_TYPE enum).
            contents: File contents (bytes, string, or file-like object).

        Returns:
            API response data.

        Raises:
            SpecificationError: If doc_content_id is not set.
            ApiError: If the API returns an error.
        """
        if not self.doc_content_id:
            raise SpecificationError(
                "content_id", "Content not finalized for inspection"
            )
        return await self._set_asset(
            f"{self.doc_content_id}/{name}", file_name, mime_type, contents
        )

    async def get_contents(self) -> Dict[str, Any]:
        """Get the inspection content manifest.

        Retrieves the manifest.json file that describes the inspection's
        content assets (e.g., generated reports).

        Returns:
            Dictionary containing the content manifest.

        Raises:
            SpecificationError: If content_id is not set (inspection not finalized).
            ApiError: If the API returns an error.
            AccQsureException: If there's an error making the request.
        """
        if not self.content_id:
            raise SpecificationError(
                "content_id", "Content not finalized for inspection"
            )

        resp = await self.accqsure._query(
            f"/inspection/{self.id}/asset/{self.content_id}/manifest.json",
            "GET",
        )
        return resp

    async def get_content_item(
        self, name: str
    ) -> Union[bytes, str, Dict[str, Any]]:
        """Get a specific content item from the inspection.

        Retrieves a named content item (file) from the inspection's assets
        (e.g., generated reports).

        Args:
            name: Name of the content item to retrieve.

        Returns:
            Content item data (bytes, string, or dict depending on content type).

        Raises:
            SpecificationError: If content_id is not set (inspection not finalized).
            ApiError: If the API returns an error.
            AccQsureException: If there's an error making the request.
        """
        if not self.content_id:
            raise SpecificationError(
                "content_id", "Content not finalized for inspection"
            )

        return await self.accqsure._query(
            f"/inspection/{self.id}/asset/{self.content_id}/{name}",
            "GET",
        )

    async def _set_content_item(
        self, name: str, file_name: str, mime_type: MIME_TYPE, contents: Any
    ) -> Any:
        """Set a content item for the inspection (internal method).

        **Note:** This method is only used internally by AccQsure and will
        return a 403 Forbidden error if attempted to be used directly by users.

        Args:
            name: Name of the content item.
            file_name: Name of the file.
            mime_type: MIME type of the content (MIME_TYPE enum).
            contents: File contents (bytes, string, or file-like object).

        Returns:
            API response data.

        Raises:
            SpecificationError: If content_id is not set.
            ApiError: If the API returns an error (including 403 Forbidden
                     if called directly by users).
        """
        if not self.content_id:
            raise SpecificationError(
                "content_id", "Content not finalized for inspection"
            )
        return await self._set_asset(
            f"{self.content_id}/{name}", file_name, mime_type, contents
        )

    async def download_report(self) -> Union[bytes, str, Dict[str, Any]]:
        """Download the inspection report.

        Retrieves the generated inspection report file. The report name
        is determined from the content manifest.

        Returns:
            Report file contents (typically bytes for PDF or other binary formats).

        Raises:
            SpecificationError: If content_id is not set (inspection not finalized).
            ApiError: If the API returns an error.
            AccQsureException: If there's an error making the request.
        """
        if not self.content_id:
            raise SpecificationError(
                "content_id", "Content not finalized for inspection"
            )
        manifest = await self.get_contents()
        return await self.get_content_item(manifest.get("report"))

    async def list_checks(
        self,
        document_id: Optional[str] = None,
        manifest_id: Optional[str] = None,
        limit: int = 50,
        start_key: Optional[str] = None,
        name: Optional[str] = None,
        **kwargs: Any,
    ) -> Tuple[List["InspectionCheck"], Optional[str]]:
        """List inspection checks.

        Retrieves a paginated list of inspection checks (validation results)
        for this inspection. Can be filtered by document, manifest, or check name.

        Args:
            document_id: Filter checks by document ID (optional).
            manifest_id: Filter checks by manifest ID (optional).
            limit: Number of results to return (default: 50, max: 100).
            start_key: Pagination cursor from previous response.
            name: Filter checks by check name (optional).
            **kwargs: Additional query parameters.

        Returns:
            Tuple of (list of InspectionCheck instances, last_key for pagination).

        Raises:
            ApiError: If the API returns an error.
            AccQsureException: If there's an error making the request.
        """
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
            InspectionCheck.from_api(self.accqsure, self.id, check)
            for check in resp.get("results")
        ]
        return checks, resp.get("last_key")


@dataclass
class InspectionCheck:
    """Represents an inspection check (validation result) in the AccQsure system.

    Inspection checks are the results of validating documents against
    manifest checks. They contain compliance status, rationale, and
    suggestions for non-compliant items.
    """

    inspection_id: str
    id: str
    section: str
    name: str
    status: str
    critical: Optional[bool] = field(default=None)
    compliant: Optional[bool] = field(default=None)
    rationale: Optional[str] = field(default=None)
    suggestion: Optional[str] = field(default=None)
    created_at: Optional[str] = field(default=None)
    updated_at: Optional[str] = field(default=None)

    @classmethod
    def from_api(
        cls, accqsure: "AccQsure", inspection_id: str, data: dict[str, Any]
    ) -> Optional["InspectionCheck"]:
        """Create an InspectionCheck instance from API response data.

        Args:
            accqsure: The AccQsure client instance.
            inspection_id: The inspection ID this check belongs to.
            data: Dictionary containing inspection check data from the API.

        Returns:
            InspectionCheck instance if data is provided, None otherwise.
        """
        if not data:
            return None
        entity = cls(
            inspection_id=inspection_id,
            id=data.get("entity_id"),
            section=data.get("check_section"),
            name=data.get("check_name"),
            status=data.get("status"),
            critical=data.get("critical"),
            compliant=data.get("compliant"),
            rationale=data.get("rationale"),
            suggestion=data.get("suggestion"),
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

    async def update(self, **kwargs: Any) -> "InspectionCheck":
        """Update the inspection check.

        Updates inspection check properties (e.g., compliant status, rationale,
        suggestion) and refreshes the instance with the latest data from the API.

        Args:
            **kwargs: Inspection check properties to update.

        Returns:
            Self for method chaining.

        Raises:
            ApiError: If the API returns an error.
            AccQsureException: If there's an error making the request.
        """
        resp = await self.accqsure._query(
            f"/inspection/{self.inspection_id}/check/{self.id}",
            "PUT",
            None,
            dict(**kwargs),
        )
        exclude = ["id", "inspection_id", "accqsure"]

        for f in fields(self.__class__):
            if (
                f.name not in exclude
                and f.init
                and resp.get(f.name) is not None
            ):  # Only update init args
                # Handle field name mapping
                field_name = f.name
                if field_name == "section":
                    setattr(self, field_name, resp.get("check_section"))
                elif field_name == "name":
                    setattr(self, field_name, resp.get("check_name"))
                else:
                    setattr(self, field_name, resp.get(field_name))
        return self

    async def refresh(self) -> "InspectionCheck":
        """Refresh the inspection check data from the API.

        Fetches the latest inspection check data from the API and updates the
        instance fields.

        Returns:
            Self for method chaining.

        Raises:
            ApiError: If the API returns an error.
            AccQsureException: If there's an error making the request.
        """
        resp = await self.accqsure._query(
            f"/inspection/{self.inspection_id}/check/{self.id}",
            "GET",
        )
        exclude = ["id", "inspection_id", "accqsure"]

        for f in fields(self.__class__):
            if (
                f.name not in exclude
                and f.init
                and resp.get(f.name) is not None
            ):  # Only update init args
                # Handle field name mapping
                field_name = f.name
                if field_name == "section":
                    setattr(self, field_name, resp.get("check_section"))
                elif field_name == "name":
                    setattr(self, field_name, resp.get("check_name"))
                else:
                    setattr(self, field_name, resp.get(field_name))
        return self
