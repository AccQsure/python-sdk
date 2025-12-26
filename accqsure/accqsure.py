import json
import os
import aiohttp
import logging
import traceback
import math
import asyncio
import io
from pathlib import Path
from importlib.metadata import version
from typing import Optional, Dict, Any, Union, List

from accqsure.auth import Auth
from accqsure.text import Text
from accqsure.document_types import DocumentTypes
from accqsure.documents import Documents
from accqsure.manifests import Manifests
from accqsure.inspections import Inspections
from accqsure.plots import Plots
from accqsure.charts import Charts
from accqsure.util import Utilities

from accqsure.exceptions import (
    ApiError,
    AccQsureException,
    SpecificationError,
    TaskError,
)


DEFAULT_CONFIG_DIR = "~/.accqsure"
DEFAULT_CREDENTIAL_FILE_NAME = "credentials.json"


class AccQsure(object):
    """Main client class for the AccQsure Python SDK.

    This is the primary entry point for interacting with the AccQsure API.
    It provides access to all resource managers (documents, inspections, etc.)
    and handles authentication and HTTP communication.

    Example:
        ```python
        from accqsure import AccQsure

        client = AccQsure()
        documents = await client.documents.list(document_type_id="...")
        ```
    """

    def __init__(self, **kwargs: Any) -> None:
        """Initialize the AccQsure client.

        Args:
            **kwargs: Optional keyword arguments:
                - config_dir: Directory path for storing configuration and cached tokens.
                             Defaults to ~/.accqsure or ACCQSURE_CONFIG_DIR environment variable.
                - credentials_file: Path to the credentials JSON file.
                                   Defaults to {config_dir}/credentials.json or
                                   ACCQSURE_CREDENTIALS_FILE environment variable.
                - key: Optional dictionary containing authentication credentials.
                       If not provided, credentials will be loaded from credentials_file.
        """

        self._version = version("accqsure")
        config_dir = (
            Path(kwargs.get("config_dir")).expanduser().resolve()
            if kwargs.get("config_dir")
            else Path(
                os.environ.get("ACCQSURE_CONFIG_DIR") or DEFAULT_CONFIG_DIR
            )
            .expanduser()
            .resolve()
        )
        credentials_file = (
            Path(kwargs.get("credentials_file")).expanduser().resolve()
            if kwargs.get("credentials_file")
            else Path(
                os.environ.get("ACCQSURE_CREDENTIALS_FILE")
                or f"{config_dir}/{DEFAULT_CREDENTIAL_FILE_NAME}"
            )
            .expanduser()
            .resolve()
        )

        self.auth = Auth(
            config_dir=config_dir,
            credentials_file=credentials_file,
            key=kwargs.get("key", None),
        )
        self.text = Text(self)
        self.document_types = DocumentTypes(self)
        self.documents = Documents(self)
        self.manifests = Manifests(self)
        self.inspections = Inspections(self)
        self.plots = Plots(self)
        self.charts = Charts(self)
        self.util = Utilities()

    @property
    def __version__(self) -> str:
        """Get the SDK version string.

        Returns:
            The version string of the installed SDK package.
        """
        return self._version

    async def _query(
        self,
        path: str,
        method: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[
            Union[Dict[str, Any], List[Any], str, bytes, io.IOBase]
        ] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Union[Dict[str, Any], str, bytes]:
        """Make an authenticated HTTP request to the AccQsure API.

        This is an internal method used by all resource managers to make
        API calls. It handles authentication, request serialization, and
        response parsing.

        Args:
            path: API endpoint path (e.g., "/document/{id}").
            method: HTTP method (GET, POST, PUT, DELETE, etc.).
            params: Optional query parameters as a dictionary.
            data: Optional request body. Can be a dict, list, string, bytes,
                  or file-like object. Will be serialized to JSON if dict/list.
            headers: Optional additional HTTP headers.

        Returns:
            Response data. Returns a dict for JSON responses, str for text
            responses, or bytes for binary responses.

        Raises:
            AccQsureException: If authentication fails or there's an error
                getting the access token.
            ApiError: If the API returns a 4xx or 5xx status code.
        """
        try:
            token = await self.auth.get_token()
        except AccQsureException as e:
            raise e
        except Exception as e:
            raise AccQsureException(
                f"Error getting authorization tokens.  Verify configured credentials. Error: {traceback.format_exc()}"
            ) from e
        logging.debug(
            "Call parameters - Path: %s, Method: %s, Params: %s, Body: %s, Headers: %s",
            path,
            method,
            params,
            data,
            headers,
        )
        api_endpoint = token.api_endpoint
        headers = (
            {
                **headers,
                **{
                    "Authorization": f"Bearer {token.access_token}",
                    "User-Agent": f"python-sdk/{self._version}",
                },
            }
            if headers
            else {
                "Authorization": f"Bearer {token.access_token}",
                "User-Agent": f"python-sdk/{self._version}",
            }
        )
        if params:
            if not isinstance(params, dict):
                raise AccQsureException(
                    "Query parameters must be a valid dictionary"
                )
            params = {
                k: (str(v).lower() if isinstance(v, bool) else v)
                for k, v in params.items()
                if v is not None
            }  ## aiohttp doesn't support boolean

        if "Content-Type" not in headers:
            headers["Content-Type"] = "application/json"

        if headers["Content-Type"] == "application/json" and data is not None:
            if isinstance(data, (dict, list, bool, type(None))):
                # Serialize Python objects to JSON string
                data = json.dumps(data)
            if isinstance(data, str):
                # Encode string to bytes
                data = data.encode("utf-8")
            if isinstance(data, (bytes, bytearray)):
                # Wrap bytes in BytesIO to avoid event loop warning
                data = io.BytesIO(data)
            # If data is io.IOBase (e.g., BytesIO, open file), pass as-is for streaming

        url = f"{api_endpoint}/v1{path}"

        logging.debug(
            "Request - Url: %s, Method: %s, Params: %s, Body: %s, Headers: %s",
            url,
            method,
            params,
            data,
            headers,
        )
        async with aiohttp.ClientSession() as session:
            async with session.request(
                method,
                url,
                data=data,
                headers=headers,
                params=params,
            ) as resp:
                if (resp.status // 100) in [4, 5]:
                    what = await resp.read()
                    content_type = resp.headers.get("content-type", "")
                    resp.close()
                    if content_type == "application/json":
                        raise ApiError(
                            resp.status, json.loads(what.decode("utf8"))
                        )
                    else:
                        raise ApiError(
                            resp.status, {"message": what.decode("utf8")}
                        )
                content_type = resp.headers.get("Content-Type", "").lower()
                if "application/json" in content_type:
                    return await resp.json()
                elif "text" in content_type:
                    return await resp.text()
                else:
                    return await resp.read()

    async def _query_stream(
        self,
        path: str,
        method: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> str:
        """Make an authenticated streaming HTTP request to the AccQsure API.

        This method is used for streaming responses, such as text generation
        endpoints that return Server-Sent Events (SSE). It processes the
        stream line by line and accumulates the response content.

        Args:
            path: API endpoint path (e.g., "/text/generate").
            method: HTTP method (typically POST for streaming endpoints).
            params: Optional query parameters as a dictionary.
            data: Optional request body as a dictionary (will be JSON serialized).
            headers: Optional additional HTTP headers.

        Returns:
            Accumulated response content as a string. For text generation,
            this is the complete generated text.

        Raises:
            AccQsureException: If authentication fails or there's an error
                getting the access token.
            ApiError: If the API returns a 4xx or 5xx status code.
        """
        try:
            token = await self.auth.get_token()
        except AccQsureException as e:
            raise e
        except Exception as e:
            raise AccQsureException(
                f"Error getting authorization tokens.  Verify configured credentials. Error: {traceback.format_exc()}"
            ) from e
        logging.debug(
            "Call parameters - Path: %s, Method: %s, Params: %s, Body: %s, Headers: %s",
            path,
            method,
            params,
            data,
            headers,
        )
        api_endpoint = token.api_endpoint
        headers = (
            {
                **headers,
                **{
                    "Authorization": f"Bearer {token.access_token}",
                    "User-Agent": f"python-sdk/{self._version}",
                },
            }
            if headers
            else {
                "Authorization": f"Bearer {token.access_token}",
                "User-Agent": f"python-sdk/{self._version}",
            }
        )
        if params:
            if not isinstance(params, dict):
                raise AccQsureException(
                    "Query parameters must be a valid dictionary"
                )
            params = {
                k: (str(v).lower() if isinstance(v, bool) else v)
                for k, v in params.items()
                if v is not None
            }  ## aiohttp doesn't support boolean

        if "Content-Type" not in headers:
            headers["Content-Type"] = "application/json"
        url = f"{api_endpoint}/v1{path}"

        logging.debug(
            "Request - Url: %s, Method: %s, Params: %s, Body: %s, Headers: %s",
            url,
            method,
            params,
            data,
            headers,
        )
        answer = ""
        async with aiohttp.ClientSession() as session:
            async with session.request(
                method,
                url,
                data=json.dumps(data),
                headers=headers,
                params=params,
            ) as resp:
                if (resp.status // 100) in [4, 5]:
                    what = await resp.read()
                    content_type = resp.headers.get("content-type", "")
                    resp.close()
                    if content_type == "application/json":
                        raise ApiError(
                            resp.status, json.loads(what.decode("utf8"))
                        )
                    else:
                        raise ApiError(
                            resp.status, {"message": what.decode("utf8")}
                        )
                try:
                    async for line in resp.content:
                        if line and line.strip():
                            clean_line = (
                                line.decode("utf-8")
                                .removeprefix("data:")
                                .strip()
                            )
                            # pylint: disable=no-member
                            # logging.trace(clean_line)
                            if clean_line == "[DONE]":
                                continue
                            try:
                                response = json.loads(clean_line)
                            except Exception:
                                logging.error("bad line: %s", clean_line)
                                continue

                            if response.get("generated_text"):
                                # pylint: disable=no-member
                                # logging.trace("final response: %s", response)
                                return response.get("generated_text")
                            elif response.get("choices")[0].get(
                                "finish_reason"
                            ):
                                continue
                            else:
                                content = (
                                    response.get("choices")[0]
                                    .get("delta")
                                    .get("content")
                                )
                                answer += content
                    return answer
                except Exception as e:
                    logging.exception("Error during generation response")
                    data = await resp.text()
                    logging.error("Response error: %s", data)
                    raise e

    async def _query_all(
        self,
        path: str,
        method: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> List[Dict[str, Any]]:
        """Fetch all results from a paginated API endpoint.

        This method automatically handles pagination by following the
        'last_key' cursor in API responses. It makes multiple requests
        until all results are retrieved.

        Args:
            path: API endpoint path (e.g., "/document").
            method: HTTP method (typically GET for list endpoints).
            params: Optional query parameters. A default limit of 100
                   will be set if not provided.
            data: Optional request body.
            headers: Optional additional HTTP headers.

        Returns:
            List of all result dictionaries from all pages.

        Raises:
            AccQsureException: If authentication fails.
            ApiError: If the API returns an error.
        """
        all_results = []
        params = params or {}  # Ensure params is a dict
        params["limit"] = params.get(
            "limit", 100
        )  # Set default limit if not provided
        cursor = None

        while True:
            # Update params with the current cursor (start_key)
            if cursor:
                params["start_key"] = cursor
            else:
                params.pop("start_key", None)  # Remove start_key if no cursor

            # Make the API call
            resp = await self._query(
                path=path,
                method=method,
                params=params,
                data=data,
                headers=headers,
            )

            # Extract results and cursor
            results = resp.get("results", [])
            all_results.extend(results)
            cursor = resp.get("last_key")

            # Break if no more cursor
            if not cursor:
                break

        return all_results

    async def _poll_task(
        self, task_id: str, timeout: int = 300
    ) -> Optional[Dict[str, Any]]:
        """Poll a task until it completes, fails, or times out.

        This method polls the task status endpoint at regular intervals
        until the task reaches a terminal state (finished, failed, or canceled).
        The polling interval is automatically calculated based on the timeout.

        Args:
            task_id: The task ID to poll (24-character string).
            timeout: Maximum time to wait in seconds. Defaults to 300 (5 minutes).
                    Must be less than 86400 (24 hours).

        Returns:
            Task result dictionary if the task finished successfully, None otherwise.

        Raises:
            SpecificationError: If timeout exceeds the maximum allowed value.
            TaskError: If the task fails or is canceled.
            AccQsureException: If the task times out before completion.
            ApiError: If the API returns an error when polling.
        """
        MAX_TIMEOUT = 24 * 60 * 60
        if timeout > MAX_TIMEOUT:
            raise SpecificationError(
                "timeout",
                f"timeout must be less than {MAX_TIMEOUT} seconds.",
            )

        POLL_INTERVAL_MIN = 5
        POLL_INTERVAL_MAX = 60
        POLL_INTERVAL = max(
            min(timeout / 60, POLL_INTERVAL_MAX), POLL_INTERVAL_MIN
        )
        retry_count = math.ceil(timeout / POLL_INTERVAL)
        count = 0
        while count < retry_count:
            await asyncio.sleep(POLL_INTERVAL)

            resp = await self._query(
                f"/task/{task_id}",
                "GET",
            )

            status = resp.get("status")
            if status == "finished":
                return resp.get("result")
            if status in ["failed", "canceled"]:
                raise TaskError(resp.get("result"))

            count += 1

        raise AccQsureException(f"Timeout waiting for task {task_id}")
