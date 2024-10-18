import base64
import json
import aiofiles
import aiohttp
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from cryptography.hazmat.backends import default_backend
import time
import os
import logging
from urllib.parse import urlparse

from accqsure.exceptions import AccQsureException


class Token(object):
    def __init__(
        self,
        organization_id: str,
        access_token: str,
        expires_at: int,
        api_endpoint: str,
    ):
        self.organization_id = organization_id
        self.access_token = access_token
        self.expires_at = expires_at
        self.api_endpoint = api_endpoint

    def to_json(self) -> str:
        return json.dumps(self.__dict__, indent=2, ensure_ascii=False)

    @classmethod
    def from_json(cls, json_str: str):
        data = json.loads(json_str)
        return cls(**data)

    def __repr__(self) -> str:
        return self.to_json()


def base64_to_base64_url(data):
    return data.replace("=", "").replace("+", "-").replace("/", "_")


async def sign_jwt(alg, kid, aud, iss, sub, exp, payload, private_key_pem):
    header = {
        "alg": alg,
        "kid": kid,
        "typ": "JWT",
    }

    full_payload = {
        **payload,
        "iat": int(time.time()),
        "exp": exp,
        "iss": iss,
        "sub": sub,
        "aud": aud,
    }

    partial_token = f"{base64_to_base64_url(base64.b64encode(json.dumps(header).encode()).decode())}.{base64_to_base64_url(base64.b64encode(json.dumps(full_payload).encode()).decode())}"

    private_key = load_pem_private_key(
        private_key_pem.encode(), password=None, backend=default_backend()
    )

    if alg == "EdDSA":
        signature = private_key.sign(partial_token.encode())
    else:
        raise ValueError("Unsupported algorithm")

    signed_token = (
        f"{partial_token}.{base64_to_base64_url(base64.b64encode(signature).decode())}"
    )
    return signed_token


async def get_access_token(key):

    try:
        token = await sign_jwt(
            "EdDSA",
            key["key_id"],
            key["auth_uri"],
            key["client_id"],
            key["client_id"],
            int(time.time()) + 3600,
            {"organization_id": key["organization_id"]},
            key["private_key"],
        )
    except Exception as error:
        raise AccQsureException(f"Error signing client JWT {error}")

    async with aiohttp.ClientSession() as session:
        async with session.post(
            key["auth_uri"],
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data={
                "grant_type": "client_credentials",
                "client_id": key["client_id"],
                "scope": "admin",
                "client_assertion_type": "urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
                "client_assertion": token,
            },
        ) as resp:
            try:
                access_token = await resp.json()
            except:
                error = resp.text
                raise AccQsureException(f"Error fetching access token {error}")

    api_url = urlparse(key["auth_uri"])
    return dict(
        organization_id=key["organization_id"],
        access_token=access_token["access_token"],
        expires_at=access_token["expires_at"],
        api_endpoint=f"{api_url.scheme}://{api_url.netloc}",
    )


async def load_cached_token(token_file_path):
    if not os.path.exists(token_file_path):
        return None

    async with aiofiles.open(token_file_path, mode="r", encoding="utf8") as f:
        try:
            raw = await f.read()
            data = Token.from_json(raw)
            return data
        except json.JSONDecodeError:
            return None


async def save_token(token_file_path: str, token: Token):
    os.makedirs(os.path.dirname(token_file_path), exist_ok=True)
    async with aiofiles.open(token_file_path, "w") as f:
        await f.write(token.to_json())
    os.chmod(token_file_path, 0o600)


def is_token_valid(token: Token):
    if not token:
        logging.debug(f"Token absent")
        return False
    logging.debug(f"Token expires: {token.expires_at}")
    return (token.expires_at - 60) > time.time()


class Auth(object):
    def __init__(self, config_dir: str, credentials_file: str, **kwargs):
        self.token_file_path = f"{config_dir}/token.json"
        self.credentials_file = credentials_file
        self.token = None
        self.key = None

    async def get_new_token(self):
        if not self.key:
            try:
                async with aiofiles.open(
                    self.credentials_file, mode="r", encoding="utf8"
                ) as f:
                    data = await f.read()

                self.key = json.loads(data)
            except FileNotFoundError:
                raise AccQsureException(
                    f"AccQsure credentials file {self.credentials_file} not found"
                )
        token = await get_access_token(self.key)
        logging.debug(f"Token Response {token}")
        self.token = Token(**token)
        logging.debug(f"New Token {self.token}")
        await save_token(self.token_file_path, self.token)

    async def get_token(self):
        if is_token_valid(self.token):
            logging.debug(f"Token is valid")
            return self.token
        else:
            if not self.token:
                logging.debug(f"Checking cached token")
                token = await load_cached_token(self.token_file_path)
                if is_token_valid(token):
                    self.token = token
                else:
                    await self.get_new_token()
            else:
                await self.get_new_token()

        logging.debug(f"Token expires: {self.token.expires_at}")

        return self.token
