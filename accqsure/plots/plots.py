from __future__ import annotations
from dataclasses import dataclass, field, fields
from typing import Optional, Any, TYPE_CHECKING, List, Tuple, Union, Dict
import logging

from accqsure.exceptions import SpecificationError
from accqsure.enums import MIME_TYPE
from .sections import PlotSections
from .waypoints import PlotWaypoints

if TYPE_CHECKING:
    from accqsure import AccQsure


class Plots(object):
    """Manager for plot resources.

    Provides methods to create, retrieve, list, and delete plots.
    Plots are generated documents based on charts. Maps to the
    /v1/plot API endpoints.
    """

    def __init__(self, accqsure: "AccQsure") -> None:
        """Initialize the Plots manager.

        Args:
            accqsure: The AccQsure client instance.
        """
        self.accqsure = accqsure

    async def get(self, id_: str, **kwargs: Any) -> Optional["Plot"]:
        """Get a plot by ID.

        Retrieves a single plot by its entity ID.

        Args:
            id_: Plot entity ID (24-character string).
            **kwargs: Additional query parameters.

        Returns:
            Plot instance if found, None otherwise.

        Raises:
            ApiError: If the API returns an error.
            AccQsureException: If there's an error making the request.
        """
        resp = await self.accqsure._query(f"/plot/{id_}", "GET", kwargs)
        return Plot.from_api(self.accqsure, resp)

    async def list(
        self,
        limit: int = 50,
        start_key: Optional[str] = None,
        fetch_all: bool = False,
        **kwargs: Any,
    ) -> Union[List["Plot"], Tuple[List["Plot"], Optional[str]]]:
        """List plots.

        Retrieves a list of plots.
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
            If fetch_all is True: List of all Plot instances.
            If fetch_all is False: Tuple of (list of Plot instances,
                                          last_key for pagination).

        Raises:
            ApiError: If the API returns an error.
            AccQsureException: If there's an error making the request.
        """
        if fetch_all:
            resp = await self.accqsure._query_all(
                "/plot",
                "GET",
                {**kwargs},
            )
            plots = [Plot.from_api(self.accqsure, plot) for plot in resp]
            return plots
        else:
            resp = await self.accqsure._query(
                "/plot",
                "GET",
                {"limit": limit, "start_key": start_key, **kwargs},
            )
            plots = [
                Plot.from_api(self.accqsure, plot) for plot in resp.get("results")
            ]
            return plots, resp.get("last_key")

    async def create(
        self,
        name: str,
        record_id: str,
        chart_id: str,
        **kwargs: Any,
    ) -> "Plot":
        """Create a new plot.

        Creates a new plot with the specified name, record ID, and chart ID.
        Plots are generated documents based on charts.

        Args:
            name: Name of the plot.
            record_id: Record ID associated with this plot.
            chart_id: Chart ID to use as a template for this plot.
            **kwargs: Additional plot properties.

        Returns:
            Created Plot instance.

        Raises:
            ApiError: If the API returns an error (e.g., validation error).
            AccQsureException: If there's an error making the request.
        """
        data = dict(
            name=name,
            record_id=record_id,
            chart_id=chart_id,
            **kwargs,
        )
        payload = {k: v for k, v in data.items() if v is not None}
        logging.info("Creating Plot %s", name)

        resp = await self.accqsure._query("/plot", "POST", None, payload)
        plot = Plot.from_api(self.accqsure, resp)
        logging.info("Created Plot %s with id %s", name, plot.id)

        return plot

    async def remove(self, id_: str, **kwargs: Any) -> None:
        """Delete a plot.

        Permanently deletes a plot by its entity ID.

        Args:
            id_: Plot entity ID (24-character string).
            **kwargs: Additional query parameters.

        Raises:
            ApiError: If the API returns an error (e.g., plot not found).
            AccQsureException: If there's an error making the request.
        """
        await self.accqsure._query(f"/plot/{id_}", "DELETE", {**kwargs})


@dataclass
class Plot:
    """Represents a plot in the AccQsure system.

    Plots are generated documents based on charts. They contain sections,
    waypoints, and generated content. Plots are created from charts and
    can be finalized to produce document content.
    """

    id: str
    name: str
    record_id: str
    status: str
    created_at: Optional[str] = field(default=None)
    updated_at: Optional[str] = field(default=None)
    content_id: Optional[str] = field(default=None)

    sections: PlotSections = field(
        init=False, repr=False, compare=False, hash=False
    )
    waypoints: PlotWaypoints = field(
        init=False, repr=False, compare=False, hash=False
    )

    @classmethod
    def from_api(
        cls, accqsure: "AccQsure", data: dict[str, Any]
    ) -> Optional["Plot"]:
        """Create a Plot instance from API response data.

        Args:
            accqsure: The AccQsure client instance.
            data: Dictionary containing plot data from the API.

        Returns:
            Plot instance if data is provided, None otherwise.
        """
        if not data:
            return None
        entity = cls(
            id=data.get("entity_id"),
            name=data.get("name"),
            record_id=data.get("record_id"),
            status=data.get("status"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
            content_id=data.get("content_id"),
        )
        entity.accqsure = accqsure
        entity.sections = PlotSections(entity.accqsure, entity.id)
        entity.waypoints = PlotWaypoints(entity.accqsure, entity.id)
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
        """Delete this plot.

        Permanently deletes the plot from the system.

        Raises:
            ApiError: If the API returns an error.
            AccQsureException: If there's an error making the request.
        """
        await self.accqsure._query(
            f"/plot/{self.id}",
            "DELETE",
        )

    async def rename(self, name: str) -> "Plot":
        """Rename the plot.

        Updates the plot's name and refreshes the instance with the
        latest data from the API.

        Args:
            name: New name for the plot.

        Returns:
            Self for method chaining.

        Raises:
            ApiError: If the API returns an error.
            AccQsureException: If there's an error making the request.
        """
        resp = await self.accqsure._query(
            f"/plot/{self.id}",
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

    async def refresh(self) -> "Plot":
        """Refresh the plot data from the API.

        Fetches the latest plot data from the API and updates the
        instance fields.

        Returns:
            Self for method chaining.

        Raises:
            ApiError: If the API returns an error.
            AccQsureException: If there's an error making the request.
        """
        resp = await self.accqsure._query(
            f"/plot/{self.id}",
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

    async def _set_asset(
        self, path: str, file_name: str, mime_type: MIME_TYPE, contents: Any
    ) -> Any:
        """Set an asset file for the plot (internal method).

        Args:
            path: Asset path within the plot.
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
            f"/plot/{self.id}/asset/{path}",
            "PUT",
            params={"file_name": file_name},
            data=contents,
            headers={"Content-Type": mime_type_str},
        )

    async def get_contents(self) -> Dict[str, Any]:
        """Get the plot content manifest.

        Retrieves the manifest.json file that describes the plot's
        content assets (e.g., generated documents).

        Returns:
            Dictionary containing the content manifest.

        Raises:
            SpecificationError: If content_id is not set (plot not finalized).
            ApiError: If the API returns an error.
            AccQsureException: If there's an error making the request.
        """
        if not self.content_id:
            raise SpecificationError(
                "content_id", "Content not finalized for plot"
            )

        resp = await self.accqsure._query(
            f"/plot/{self.id}/asset/manifest.json",
            "GET",
        )
        return resp

    async def get_content_item(
        self, name: str
    ) -> Union[bytes, str, Dict[str, Any]]:
        """Get a specific content item from the plot.

        Retrieves a named content item (file) from the plot's assets
        (e.g., generated documents).

        Args:
            name: Name of the content item to retrieve.

        Returns:
            Content item data (bytes, string, or dict depending on content type).

        Raises:
            SpecificationError: If content_id is not set (plot not finalized).
            ApiError: If the API returns an error.
            AccQsureException: If there's an error making the request.
        """
        if not self.content_id:
            raise SpecificationError(
                "content_id", "Content not finalized for plot"
            )

        return await self.accqsure._query(
            f"/plot/{self.id}/asset/{name}",
            "GET",
        )

    async def _set_content_item(
        self, name: str, file_name: str, mime_type: MIME_TYPE, contents: Any
    ) -> Any:
        """Set a content item for the plot (internal method).

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
                "content_id", "Content not finalized for plot"
            )
        return await self._set_asset(f"{name}", file_name, mime_type, contents)
