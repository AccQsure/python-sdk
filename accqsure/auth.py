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
from typing import Optional, Dict, Any

from accqsure.exceptions import AccQsureException


class Token(object):
    """Represents an OAuth2 access token for AccQsure API authentication.

    This class stores the access token, organization ID, expiration time,
    and API endpoint. Tokens are used to authenticate requests to the API.
    """

    def __init__(
        self,
        organization_id: str,
        access_token: str,
        expires_at: int,
        api_endpoint: str,
    ) -> None:
        """Initialize a Token instance.

        Args:
            organization_id: The organization ID associated with this token.
            access_token: The OAuth2 access token string.
            expires_at: Unix timestamp when the token expires.
            api_endpoint: The base URL of the API endpoint.
        """
        self.organization_id = organization_id
        self.access_token = access_token
        self.expires_at = expires_at
        self.api_endpoint = api_endpoint

    def to_json(self) -> str:
        """Serialize the token to a JSON string.

        Returns:
            JSON string representation of the token.
        """
        return json.dumps(self.__dict__, indent=2, ensure_ascii=False)

    @classmethod
    def from_json(cls, json_str: str) -> "Token":
        """Deserialize a token from a JSON string.

        Args:
            json_str: JSON string containing token data.

        Returns:
            Token instance created from the JSON data.
        """
        data = json.loads(json_str)
        return cls(**data)

    def __repr__(self) -> str:
        return self.to_json()


def base64_to_base64_url(data: str) -> str:
    """Convert base64 encoding to base64url encoding.

    Base64url encoding is URL-safe and used in JWT tokens. It replaces
    '+' with '-', '/' with '_', and removes padding '=' characters.

    Args:
        data: Base64-encoded string.

    Returns:
        Base64url-encoded string.
    """
    return data.replace("=", "").replace("+", "-").replace("/", "_")


async def sign_jwt(
    alg: str,
    kid: str,
    aud: str,
    iss: str,
    sub: str,
    exp: int,
    payload: Dict[str, Any],
    private_key_pem: str,
) -> str:
    """Sign a JWT token using EdDSA algorithm.

    Creates and signs a JWT token with the provided claims and private key.
    The token is signed using EdDSA (Edwards-curve Digital Signature Algorithm).

    Args:
        alg: JWT algorithm identifier (must be "EdDSA").
        kid: Key ID for the signing key.
        aud: Audience claim (typically the auth endpoint URI).
        iss: Issuer claim (typically the client ID).
        sub: Subject claim (typically the client ID).
        exp: Expiration time as Unix timestamp.
        payload: Additional JWT payload claims.
        private_key_pem: PEM-encoded private key for signing.

    Returns:
        Signed JWT token string.

    Raises:
        ValueError: If the algorithm is not "EdDSA".
        AccQsureException: If there's an error signing the token.
    """
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

    signed_token = f"{partial_token}.{base64_to_base64_url(base64.b64encode(signature).decode())}"
    return signed_token


async def get_access_token(key: Dict[str, str]) -> Dict[str, Any]:
    """Obtain an OAuth2 access token using client credentials grant.

    Authenticates with the AccQsure OAuth2 endpoint using a JWT bearer token
    assertion. The JWT is signed with the client's private key and includes
    the organization ID in the payload.

    This function implements the OAuth2 client credentials flow with JWT
    bearer assertion as specified in RFC 7523.

    Args:
        key: Dictionary containing authentication credentials:
            - key_id: Key ID for JWT signing
            - auth_uri: OAuth2 authorization endpoint URI
            - client_id: OAuth2 client identifier
            - organization_id: Organization ID for the token
            - private_key: PEM-encoded private key for JWT signing

    Returns:
        Dictionary containing:
            - organization_id: Organization ID
            - access_token: OAuth2 access token
            - expires_at: Token expiration timestamp
            - api_endpoint: Base API endpoint URL

    Raises:
        AccQsureException: If there's an error signing the JWT or fetching the token.
    """
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
        raise AccQsureException(f"Error signing client JWT {error}") from error

    async with aiohttp.ClientSession() as session:
        async with session.post(
            key["auth_uri"],
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data={
                "grant_type": "client_credentials",
                "client_id": key["client_id"],
                "scope": "read:documents write:documents admin internal:task",
                "client_assertion_type": "urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
                "client_assertion": token,
            },
        ) as resp:
            try:
                access_token = await resp.json()
            except Exception:
                error = await resp.text()
                raise AccQsureException(
                    f"Error fetching access token {error}"
                ) from error

    api_url = urlparse(key["auth_uri"])
    return dict(
        organization_id=key["organization_id"],
        access_token=access_token["access_token"],
        expires_at=access_token["expires_at"],
        api_endpoint=f"{api_url.scheme}://{api_url.netloc}",
    )


async def load_cached_token(token_file_path: str) -> Optional[Token]:
    """Load a cached token from the filesystem.

    Attempts to load and deserialize a token from a JSON file. Returns None
    if the file doesn't exist or contains invalid JSON.

    Args:
        token_file_path: Path to the token cache file.

    Returns:
        Token instance if successfully loaded, None otherwise.
    """
    if not os.path.exists(token_file_path):
        return None

    async with aiofiles.open(token_file_path, mode="r", encoding="utf8") as f:
        try:
            raw = await f.read()
            data = Token.from_json(raw)
            return data
        except json.JSONDecodeError:
            return None


async def save_token(token_file_path: str, token: Token) -> None:
    """Save a token to the filesystem cache.

    Serializes the token to JSON and saves it to a file with restricted
    permissions (600) for security.

    Args:
        token_file_path: Path where the token should be saved.
        token: Token instance to save.
    """
    os.makedirs(os.path.dirname(token_file_path), exist_ok=True)
    async with aiofiles.open(token_file_path, "w") as f:
        await f.write(token.to_json())
    os.chmod(token_file_path, 0o600)


def is_token_valid(token: Optional[Token]) -> bool:
    """Check if a token is valid and not expired.

    A token is considered valid if it exists and has not expired.
    A 60-second buffer is used to account for clock skew and network delays.

    Args:
        token: Token instance to validate, or None.

    Returns:
        True if the token is valid and not expired, False otherwise.
    """
    if not token:
        logging.debug("Token absent")
        return False
    logging.debug("Token expires: %s", token.expires_at)
    return (token.expires_at - 60) > time.time()


class Auth(object):
    """Handles authentication and token management for the AccQsure SDK.

    This class manages OAuth2 authentication using client credentials with
    JWT bearer assertion. It handles token caching, validation, and refresh.
    Tokens are cached to disk to avoid unnecessary authentication requests.
    """

    def __init__(
        self, config_dir: str, credentials_file: str, **kwargs: Any
    ) -> None:
        """Initialize the Auth instance.

        Args:
            config_dir: Directory path for storing cached tokens.
            credentials_file: Path to the credentials JSON file.
            **kwargs: Additional keyword arguments:
                - key: Optional dictionary containing authentication credentials.
                       If not provided, credentials will be loaded from credentials_file.
        """
        self.token_file_path = f"{config_dir}/token.json"
        self.credentials_file = credentials_file
        self.token: Optional[Token] = None
        self.key: Optional[Dict[str, str]] = kwargs.get("key", None)

    async def get_new_token(self) -> None:
        """Obtain a new access token from the OAuth2 endpoint.

        Loads credentials if not already loaded, then requests a new token
        from the OAuth2 endpoint and caches it to disk.

        Raises:
            AccQsureException: If credentials file is not found or token
                acquisition fails.
        """
        if not self.key:
            try:
                async with aiofiles.open(
                    self.credentials_file, mode="r", encoding="utf8"
                ) as f:
                    data = await f.read()

                self.key = json.loads(data)
            except FileNotFoundError as e:
                raise AccQsureException(
                    f"AccQsure credentials file {self.credentials_file} not found"
                ) from e
        token = await get_access_token(self.key)
        logging.debug("Token Response %s", token)
        self.token = Token(**token)
        logging.debug("New Token %s", self.token)
        await save_token(self.token_file_path, self.token)

    async def get_token(self) -> Token:
        """Get a valid access token, refreshing if necessary.

        Returns the current token if it's valid. Otherwise, attempts to load
        a cached token from disk. If no valid cached token exists, requests
        a new token from the OAuth2 endpoint.

        Returns:
            Valid Token instance.

        Raises:
            AccQsureException: If token acquisition fails.
        """
        if is_token_valid(self.token):
            logging.debug("Token is valid")
            return self.token
        else:
            if not self.token:
                logging.debug("Checking cached token")
                token = await load_cached_token(self.token_file_path)
                if is_token_valid(token):
                    self.token = token
                else:
                    await self.get_new_token()
            else:
                await self.get_new_token()

        logging.debug("Token expires: %s", self.token.expires_at)

        return self.token
