import json
import os
import aiohttp
import logging
import traceback
from importlib.metadata import version

from accqsure.auth import Auth
from accqsure.text import Text
from accqsure.document_types import DocumentTypes
from accqsure.documents import Documents
from accqsure.manifests import Manifests

from accqsure.exceptions import ApiError, AccQsureException


DEFAULT_CONFIG_DIR = "~/.accqsure"
DEFAULT_CREDENTIAL_FILE_NAME = "credentials.json"


class AccQsure(object):
    def __init__(self, **kwargs):
        self._version = version("accqsure")
        config_dir = kwargs.get("config_dir") or os.path.expanduser(
            os.environ.get("ACCQSURE_CONFIG_DIR") or DEFAULT_CONFIG_DIR
        )
        credentials_file = kwargs.get("credentials_file") or os.path.expanduser(
            os.environ.get("ACCQSURE_CREDENTIALS_FILE")
            or f"{config_dir}/{DEFAULT_CREDENTIAL_FILE_NAME}"
        )
        self.auth = Auth(
            config_dir=config_dir,
            credentials_file=credentials_file,
        )
        self.text = Text(self)
        self.document_types = DocumentTypes(self)
        self.documents = Documents(self)
        self.manifests = Manifests(self)

    @property
    def __version__(self) -> str:
        return self._version

    async def _query(self, path, method, params=None, data=None, headers=None):
        try:
            token = await self.auth.get_token()
        except AccQsureException as e:
            raise e
        except Exception:
            raise AccQsureException(
                f"Error getting authorization tokens.  Verify configured credentials. Error: {traceback.format_exc()}"
            )
        logging.debug(
            f"Call parameters - Path: {path}, Method: {method}, Params: {params}, Body: {data}, Headers: {headers}"
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
                raise AccQsureException("Query parameters must be a valid dictionary")
            params = {
                k: (str(v).lower() if isinstance(v, bool) else v)
                for k, v in params.items()
            }  ## aiohttp doesn't support boolean

        if "Content-Type" not in headers:
            headers["Content-Type"] = "application/json"
        url = f"{api_endpoint}/v1{path}"

        logging.debug(
            f"Request - Url: {url}, Method: {method}, Params: {params}, Body: {data}, Headers: {headers}"
        )
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
                        raise ApiError(resp.status, json.loads(what.decode("utf8")))
                    else:
                        raise ApiError(resp.status, {"message": what.decode("utf8")})
                results = await resp.json()
                return results

    async def _query_stream(self, path, method, params=None, data=None, headers=None):
        try:
            token = await self.auth.get_token()
        except AccQsureException as e:
            raise e
        except Exception:
            raise AccQsureException(
                f"Error getting authorization tokens.  Verify configured credentials. Error: {traceback.format_exc()}"
            )
        logging.debug(
            f"Call parameters - Path: {path}, Method: {method}, Params: {params}, Body: {data}, Headers: {headers}"
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
                raise AccQsureException("Query parameters must be a valid dictionary")
            params = {
                k: (str(v).lower() if isinstance(v, bool) else v)
                for k, v in params.items()
            }  ## aiohttp doesn't support boolean

        if "Content-Type" not in headers:
            headers["Content-Type"] = "application/json"
        url = f"{api_endpoint}/v1{path}"

        logging.debug(
            f"Request - Url: {url}, Method: {method}, Params: {params}, Body: {data}, Headers: {headers}"
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
                        raise ApiError(resp.status, json.loads(what.decode("utf8")))
                    else:
                        raise ApiError(resp.status, {"message": what.decode("utf8")})
                try:
                    async for line in resp.content:
                        if line and line.strip():
                            clean_line = (
                                line.decode("utf-8").removeprefix("data:").strip()
                            )
                            logging.debug(clean_line)
                            if clean_line == "[DONE]":
                                continue
                            try:
                                response = json.loads(clean_line)
                            except:
                                logging.error("bad line", clean_line)
                                continue

                            if response.get("generated_text"):
                                logging.debug("final response", response)
                                return response.get("generated_text")
                            elif response.get("choices")[0].get("finish_reason"):
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
                    logging.exception(f"Error during generation response")
                    data = await response.text()
                    logging.error(f"Response error: {data}")
                    raise e
