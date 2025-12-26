from __future__ import annotations
from dataclasses import dataclass, field, fields
from typing import Optional, Any, TYPE_CHECKING, List, Tuple, Union, Dict
import logging

from accqsure.exceptions import SpecificationError
from accqsure.documents import Document
from accqsure.enums import MIME_TYPE
from .sections import ChartSections
from .waypoints import ChartWaypoints


if TYPE_CHECKING:
    from accqsure import AccQsure


class Charts:
    """Manager for chart resources.

    Provides methods to create, retrieve, list, and delete charts.
    Charts define structured document templates with sections and waypoints.
    """

    def __init__(self, accqsure: "AccQsure") -> None:
        """Initialize the Charts manager.

        Args:
            accqsure: The AccQsure client instance.
        """
        self.accqsure = accqsure

    async def get(self, id_: str, **kwargs: Any) -> Optional["Chart"]:
        """Get a chart by ID.

        Retrieves a single chart by its entity ID.

        Args:
            id_: Chart entity ID (24-character string).
            **kwargs: Additional query parameters.

        Returns:
            Chart instance if found, None otherwise.

        Raises:
            ApiError: If the API returns an error.
            AccQsureException: If there's an error making the request.
        """
        resp = await self.accqsure._query(f"/chart/{id_}", "GET", kwargs)
        return Chart.from_api(self.accqsure, resp)

    async def list(
        self,
        document_type_id: str,
        limit: int = 50,
        start_key: Optional[str] = None,
        fetch_all: bool = False,
        **kwargs: Any,
    ) -> Union[List["Chart"], Tuple[List["Chart"], Optional[str]]]:
        """List charts filtered by document type.

        Retrieves a list of charts for a specific document type.
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
            If fetch_all is True: List of all Chart instances.
            If fetch_all is False: Tuple of (list of Chart instances,
                                          last_key for pagination).

        Raises:
            ApiError: If the API returns an error.
            AccQsureException: If there's an error making the request.
        """
        if fetch_all:
            resp = await self.accqsure._query_all(
                "/chart",
                "GET",
                {
                    "document_type_id": document_type_id,
                    **kwargs,
                },
            )
            charts = [Chart.from_api(self.accqsure, chart) for chart in resp]
            return charts
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
                Chart.from_api(self.accqsure, chart)
                for chart in resp.get("results")
            ]
            return charts, resp.get("last_key")

    async def create(
        self,
        name: str,
        document_type_id: str,
        reference_document_id: str,
        **kwargs: Any,
    ) -> "Chart":
        """Create a new chart.

        Creates a new chart with the specified document type, name, and
        reference document. Charts define structured document templates.

        Args:
            name: Name of the chart.
            document_type_id: Document type ID for the chart.
            reference_document_id: Reference document ID to use as a template.
            **kwargs: Additional chart properties.

        Returns:
            Created Chart instance.

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
        logging.info("Creating Chart %s", name)

        resp = await self.accqsure._query("/chart", "POST", None, payload)
        chart = Chart.from_api(self.accqsure, resp)
        logging.info("Created Chart %s with id %s", name, chart.id)

        return chart

    async def remove(self, id_: str, **kwargs: Any) -> None:
        """Delete a chart.

        Permanently deletes a chart by its entity ID.

        Args:
            id_: Chart entity ID (24-character string).
            **kwargs: Additional query parameters.

        Raises:
            ApiError: If the API returns an error (e.g., chart not found).
            AccQsureException: If there's an error making the request.
        """
        await self.accqsure._query(f"/chart/{id_}", "DELETE", {**kwargs})


@dataclass
class Chart:
    """Represents a chart in the AccQsure system.

    Charts define structured document templates with sections and waypoints.
    They can have a reference document that serves as a template or example.
    Charts are used to generate structured documents.
    """

    id: str
    name: str
    document_type_id: str
    status: str
    created_at: str
    updated_at: str
    reference_document: Optional[Document] = field(default=None)
    approved_by: Optional[str] = field(default=None)
    last_modified_by: Optional[str] = field(default=None)

    sections: ChartSections = field(
        init=False, repr=False, compare=False, hash=False
    )
    waypoints: ChartWaypoints = field(
        init=False, repr=False, compare=False, hash=False
    )

    @classmethod
    def from_api(
        cls, accqsure: "AccQsure", data: dict[str, Any]
    ) -> Optional["Chart"]:
        """Create a Chart instance from API response data.

        Args:
            accqsure: The AccQsure client instance.
            data: Dictionary containing chart data from the API.

        Returns:
            Chart instance if data is provided, None otherwise.
        """
        if not data:
            return None
        entity = cls(
            id=data.get("entity_id"),
            name=data.get("name"),
            status=data.get("status"),
            document_type_id=data.get("document_type_id"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
            reference_document=Document.from_api(
                accqsure=accqsure, data=data.get("reference_document")
            ),
            approved_by=data.get("approved_by"),
            last_modified_by=data.get("last_modified_by"),
        )
        entity.accqsure = accqsure
        entity.sections = ChartSections(entity.accqsure, entity.id)
        entity.waypoints = ChartWaypoints(entity.accqsure, entity.id)
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
        """Delete this chart.

        Permanently deletes the chart from the system.

        Raises:
            ApiError: If the API returns an error.
            AccQsureException: If there's an error making the request.
        """
        await self.accqsure._query(
            f"/chart/{self.id}",
            "DELETE",
        )

    async def rename(self, name: str) -> "Chart":
        """Rename the chart.

        Updates the chart's name and refreshes the instance with the
        latest data from the API.

        Args:
            name: New name for the chart.

        Returns:
            Self for method chaining.

        Raises:
            ApiError: If the API returns an error.
            AccQsureException: If there's an error making the request.
        """
        resp = await self.accqsure._query(
            f"/chart/{self.id}",
            "PUT",
            None,
            dict(name=name),
        )
        exclude = ["id", "accqsure"]

        for f in fields(self.__class__):
            if (
                f.name not in exclude and f.init and resp.get(f.name)
            ):  # Only update init args (skip derived like sections/waypoints)
                setattr(self, f.name, resp.get(f.name))
        return self

    async def refresh(self) -> "Chart":
        """Refresh the chart data from the API.

        Fetches the latest chart data from the API and updates the
        instance fields.

        Returns:
            Self for method chaining.

        Raises:
            ApiError: If the API returns an error.
            AccQsureException: If there's an error making the request.
        """
        resp = await self.accqsure._query(
            f"/chart/{self.id}",
            "GET",
        )
        exclude = ["id", "accqsure"]

        for f in fields(self.__class__):
            if (
                f.name not in exclude and f.init and resp.get(f.name)
            ):  # Only update init args (skip derived like sections/waypoints)
                setattr(self, f.name, resp.get(f.name))
        return self

    async def _set_asset(
        self, path: str, file_name: str, mime_type: MIME_TYPE, contents: Any
    ) -> Any:
        """Set an asset file for the chart (internal method).

        Args:
            path: Asset path within the chart.
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
            f"/chart/{self.id}/asset/{path}",
            "PUT",
            params={"file_name": file_name},
            data=contents,
            headers={"Content-Type": mime_type_str},
        )

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
                "Reference document not found for chart",
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
                "Reference document not found for chart",
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
