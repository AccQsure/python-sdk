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
    def __init__(self, **kwargs):
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
        return self._version

    async def _query(self, path, method, params=None, data=None, headers=None):
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
        self, path, method, params=None, data=None, headers=None
    ):
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
                    data = await response.text()
                    logging.error("Response error: %s", data)
                    raise e

    async def _query_all(
        self, path, method, params=None, data=None, headers=None
    ):
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

    async def _poll_task(self, task_id, timeout=300):
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
