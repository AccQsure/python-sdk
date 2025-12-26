from __future__ import annotations
from dataclasses import dataclass, field, fields
from typing import Optional, Any, TYPE_CHECKING, List, Tuple, Dict, Union
import logging

from accqsure.exceptions import SpecificationError
from accqsure.enums import MIME_TYPE
from accqsure.util import DocumentContents

if TYPE_CHECKING:
    from accqsure import AccQsure


class PlotMarkers(object):
    """Manager for plot marker resources.

    Provides methods to create, retrieve, list, and delete plot markers.
    Markers are content items associated with plot waypoints. Maps to the
    /v1/plot/{plot_id}/waypoint/{waypoint_id}/marker API endpoints.
    """

    def __init__(
        self,
        accqsure: "AccQsure",
        plot_id: str,
        plot_waypoint_id: str,
    ) -> None:
        """Initialize the PlotMarkers manager.

        Args:
            accqsure: The AccQsure client instance.
            plot_id: The plot ID this manager is associated with.
            plot_waypoint_id: The waypoint ID this manager is associated with.
        """
        self.accqsure = accqsure
        self.plot_id = plot_id
        self.waypoint_id = plot_waypoint_id

    async def get(self, id_: str, **kwargs: Any) -> Optional["PlotMarker"]:
        """Get a plot marker by ID.

        Retrieves a single plot marker by its entity ID.

        Args:
            id_: Plot marker entity ID (24-character string).
            **kwargs: Additional query parameters.

        Returns:
            PlotMarker instance if found, None otherwise.

        Raises:
            ApiError: If the API returns an error.
            AccQsureException: If there's an error making the request.
        """
        resp = await self.accqsure._query(
            f"/plot/{self.plot_id}/waypoint/{self.waypoint_id}/marker/{id_}",
            "GET",
            kwargs,
        )
        return PlotMarker.from_api(
            self.accqsure, self.plot_id, self.waypoint_id, resp
        )

    async def list(
        self,
        limit: int = 50,
        start_key: Optional[str] = None,
        fetch_all: bool = False,
        **kwargs: Any,
    ) -> Union[List["PlotMarker"], Tuple[List["PlotMarker"], Optional[str]]]:
        """List plot markers.

        Retrieves a list of markers for this plot waypoint.
        Can return all results or paginated results.

        Args:
            limit: Number of results to return per page (default: 50, max: 100).
                   Only used if fetch_all is False.
            start_key: Pagination cursor from previous response.
                      Only used if fetch_all is False.
            fetch_all: If True, fetches all results across all pages.
                      If False, returns paginated results.
            **kwargs: Additional query parameters.

        Returns:
            If fetch_all is True: List of all PlotMarker instances.
            If fetch_all is False: Tuple of (list of PlotMarker instances,
                                          last_key for pagination).

        Raises:
            ApiError: If the API returns an error.
            AccQsureException: If there's an error making the request.
        """
        if fetch_all:
            resp = await self.accqsure._query_all(
                f"/plot/{self.plot_id}/waypoint/{self.waypoint_id}/marker",
                "GET",
                {**kwargs},
            )
            plot_markers = [
                PlotMarker.from_api(
                    self.accqsure, self.plot_id, self.waypoint_id, plot_marker
                )
                for plot_marker in resp
            ]
            return plot_markers
        else:
            resp = await self.accqsure._query(
                f"/plot/{self.plot_id}/waypoint/{self.waypoint_id}/marker",
                "GET",
                {"limit": limit, "start_key": start_key, **kwargs},
            )
            plot_markers = [
                PlotMarker.from_api(
                    self.accqsure, self.plot_id, self.waypoint_id, plot_marker
                )
                for plot_marker in resp.get("results")
            ]
            return plot_markers, resp.get("last_key")

    async def create(
        self,
        name: str,
        contents: DocumentContents,
        **kwargs: Any,
    ) -> "PlotMarker":
        """Create a new plot marker.

        Creates a new marker in this plot waypoint with the specified
        name and contents.

        Args:
            name: Name of the marker.
            contents: DocumentContents dictionary containing marker contents
                    (e.g., from Utilities.prepare_document_contents()).
            **kwargs: Additional marker properties.

        Returns:
            Created PlotMarker instance.

        Raises:
            ApiError: If the API returns an error (e.g., validation error).
            AccQsureException: If there's an error making the request.
        """
        data = dict(
            name=name,
            contents=contents,
            **kwargs,
        )
        payload = {k: v for k, v in data.items() if v is not None}
        logging.info("Creating Plot Marker %s", name)

        resp = await self.accqsure._query(
            f"/plot/{self.plot_id}/waypoint/{self.waypoint_id}/marker",
            "POST",
            None,
            payload,
        )
        plot_marker = PlotMarker.from_api(
            self.accqsure, self.plot_id, self.waypoint_id, resp
        )
        logging.info("Created Plot Marker %s with id %s", name, plot_marker.id)

        return plot_marker

    async def remove(self, id_: str, **kwargs: Any) -> None:
        """Delete a plot marker.

        Permanently deletes a plot marker by its entity ID.

        Args:
            id_: Plot marker entity ID (24-character string).
            **kwargs: Additional query parameters.

        Raises:
            ApiError: If the API returns an error (e.g., marker not found).
            AccQsureException: If there's an error making the request.
        """
        await self.accqsure._query(
            f"/plot/{self.plot_id}/waypoint/{self.waypoint_id}/marker/{id_}",
            "DELETE",
            {**kwargs},
        )


@dataclass
class PlotMarker:
    """Represents a marker within a plot waypoint.

    Markers are content items associated with plot waypoints. They contain
    generated or uploaded content and have a status indicating their state.
    """

    plot_id: str
    waypoint_id: str
    id: str
    name: str
    status: str
    created_at: Optional[str] = field(default=None)
    updated_at: Optional[str] = field(default=None)
    content_id: Optional[str] = field(default=None)

    @classmethod
    def from_api(
        cls,
        accqsure: "AccQsure",
        plot_id: str,
        waypoint_id: str,
        data: dict[str, Any],
    ) -> Optional["PlotMarker"]:
        """Create a PlotMarker instance from API response data.

        Args:
            accqsure: The AccQsure client instance.
            plot_id: The plot ID this marker belongs to.
            waypoint_id: The waypoint ID this marker belongs to.
            data: Dictionary containing plot marker data from the API.

        Returns:
            PlotMarker instance if data is provided, None otherwise.
        """
        if not data:
            return None
        entity = cls(
            plot_id=plot_id,
            waypoint_id=waypoint_id,
            id=data.get("entity_id"),
            name=data.get("name"),
            status=data.get("status"),
            content_id=data.get("content_id"),
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
        """Delete this plot marker.

        Permanently deletes the plot marker from the system.

        Raises:
            ApiError: If the API returns an error.
            AccQsureException: If there's an error making the request.
        """
        await self.accqsure._query(
            f"/plot/{self.plot_id}/waypoint/{self.waypoint_id}/marker/{self.id}",
            "DELETE",
        )

    async def rename(self, name: str) -> "PlotMarker":
        """Rename the plot marker.

        Updates the plot marker's name and refreshes the instance with the
        latest data from the API.

        Args:
            name: New name for the plot marker.

        Returns:
            Self for method chaining.

        Raises:
            ApiError: If the API returns an error.
            AccQsureException: If there's an error making the request.
        """
        resp = await self.accqsure._query(
            f"/plot/{self.plot_id}/waypoint/{self.waypoint_id}/marker/{self.id}",
            "PUT",
            None,
            dict(name=name),
        )
        exclude = ["id", "plot_id", "waypoint_id", "accqsure"]

        for f in fields(self.__class__):
            if (
                f.name not in exclude
                and f.init
                and resp.get(f.name) is not None
            ):  # Only update init args
                setattr(self, f.name, resp.get(f.name))
        return self

    async def refresh(self) -> "PlotMarker":
        """Refresh the plot marker data from the API.

        Fetches the latest plot marker data from the API and updates the
        instance fields.

        Returns:
            Self for method chaining.

        Raises:
            ApiError: If the API returns an error.
            AccQsureException: If there's an error making the request.
        """
        resp = await self.accqsure._query(
            f"/plot/{self.plot_id}/waypoint/{self.waypoint_id}/marker/{self.id}",
            "GET",
        )
        exclude = ["id", "plot_id", "waypoint_id", "accqsure"]

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
        """Set an asset file for the plot marker (internal method).

        Args:
            path: Asset path within the plot marker.
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
            f"/plot/{self.plot_id}/waypoint/{self.waypoint_id}/marker/{self.id}/asset/{path}",
            "PUT",
            params={"file_name": file_name},
            data=contents,
            headers={"Content-Type": mime_type_str},
        )

    async def get_contents(self) -> Dict[str, Any]:
        """Get the plot marker content manifest.

        Retrieves the manifest.json file that describes the plot marker's
        content assets.

        Returns:
            Dictionary containing the content manifest.

        Raises:
            SpecificationError: If content_id is not set (content not ready).
            ApiError: If the API returns an error.
            AccQsureException: If there's an error making the request.
        """
        if not self.content_id:
            raise SpecificationError(
                "content_id", "Content not ready for plot marker"
            )

        resp = await self.accqsure._query(
            f"/plot/{self.plot_id}/waypoint/{self.waypoint_id}/marker/{self.id}/asset/manifest.json",
            "GET",
        )
        return resp

    async def get_content_item(
        self, name: str
    ) -> Union[bytes, str, Dict[str, Any]]:
        """Get a specific content item from the plot marker.

        Retrieves a named content item (file) from the plot marker's assets.

        Args:
            name: Name of the content item to retrieve.

        Returns:
            Content item data (bytes, string, or dict depending on content type).

        Raises:
            SpecificationError: If content_id is not set (content not ready).
            ApiError: If the API returns an error.
            AccQsureException: If there's an error making the request.
        """
        if not self.content_id:
            raise SpecificationError(
                "content_id", "Content not ready for plot marker"
            )

        return await self.accqsure._query(
            f"/plot/{self.plot_id}/waypoint/{self.waypoint_id}/marker/{self.id}/asset/{name}",
            "GET",
        )

    async def _set_content_item(
        self, name: str, file_name: str, mime_type: MIME_TYPE, contents: Any
    ) -> Any:
        """Set a content item for the plot marker (internal method).

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
                "content_id", "Content not ready for plot marker"
            )
        return await self._set_asset(name, file_name, mime_type, contents)
