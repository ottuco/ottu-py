import typing

import httpx
from httpx import Auth, BasicAuth as _BasicAuth, Request

try:
    from django.core.cache import cache  # pragma: no cover
except ImportError:  # pragma: no cover
    cache = None  # pragma: no cover


class BasicAuth(_BasicAuth):
    def __bool__(self):
        """
        Sample Pseudo Code:
            token = username:password
            encoded_token = encode(token)
            header = f"Basic {encoded_token}"

        Explanation:
            The `token` contains at least 1 character, which is colon `:`.
            The word `Basic` is 5 characters long.
            White space is 1 character long.
            In total, the length of the header is 7 + len(token).
        """
        return len(self._auth_header) > 7


class BasicAuthorizationHeaderAuth(Auth):
    """
    Basic authentication using `Authorization` header.
    """

    def __init__(self, header: str):
        self.header = header

    def auth_flow(self, request: Request):
        request.headers["Authorization"] = self.header
        yield request

    def __bool__(self):
        return bool(self.header)


class TokenAuth(BasicAuthorizationHeaderAuth):
    def __init__(self, token: str, prefix: str = "Bearer"):
        self.prefix = prefix
        self.token = token
        header = f"{self.prefix} {self.token}".strip()
        super().__init__(header=header)

    def __bool__(self):
        return bool(self.token)


class APIKeyAuth(TokenAuth):
    def __init__(self, api_key: str, prefix: str = "Api-Key"):
        super().__init__(token=api_key, prefix=prefix)


class KeycloakAuthBase:
    grant_type: str
    namespace = "keycloak"

    def __init__(
        self,
        host: str,
        realm: str,
        caching: bool = False,
        cache_key="acc_tok",
        *args,
        **kwargs,
    ):
        self.host = host
        self.realm = realm
        self.caching = caching
        self.cache_key = cache_key

    @property
    def token_url(self) -> str:
        return (
            f"https://{self.host}/auth/realms/"
            f"{self.realm}/protocol/openid-connect/token"
        )

    @property
    def cache_key_full(self) -> str:
        return f"{self.namespace}:{self.realm}:{self.cache_key}"

    def get_token_request_payload(self) -> dict:
        return {"grant_type": self.grant_type}

    def _get_token(self):
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        data = self.get_token_request_payload()
        response = httpx.post(url=self.token_url, data=data, headers=headers)
        response.raise_for_status()
        response_json = response.json()
        access_token = response_json["access_token"]
        ttl = response_json["expires_in"]
        return access_token, ttl

    def get_token_from_cache(self):
        if cache is None:
            # During unittests, the `cache` is always available
            return None  # pragma: no cover
        return cache.get(self.cache_key_full)

    def set_token_in_cache(self, token: str, ttl: int):
        if cache is None:
            # During unittests, the `cache` is always available
            return None  # pragma: no cover
        cache.set(self.cache_key_full, token, timeout=ttl)

    def get_token(self) -> str:
        if self.caching:
            token = self.get_token_from_cache()
            if token:
                return token
        token, ttl = self._get_token()
        if self.caching:
            self.set_token_in_cache(token, ttl)
        return token

    def auth_flow(self, request: Request):
        access_token = self.get_token()
        request.headers["Authorization"] = f"Bearer {access_token}"
        yield request


class KeycloakPasswordAuth(KeycloakAuthBase, Auth):
    grant_type = "password"

    def __init__(
        self,
        username: str,
        password: str,
        client_id: str,
        client_secret: typing.Optional[str] = None,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.username = username
        self.password = password
        self.client_id = client_id
        self.client_secret = client_secret

    def get_token_request_payload(self) -> dict:
        payload = super().get_token_request_payload()
        payload["username"] = self.username
        payload["password"] = self.password
        payload["client_id"] = self.client_id
        if self.client_secret:
            payload["client_secret"] = self.client_secret
        return payload


class KeycloakClientAuth(KeycloakAuthBase, Auth):
    grant_type = "client_credentials"

    def __init__(self, client_id: str, client_secret: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client_id = client_id
        self.client_secret = client_secret

    def get_token_request_payload(self) -> dict:
        payload = super().get_token_request_payload()
        payload["client_id"] = self.client_id
        payload["client_secret"] = self.client_secret
        return payload

    def auth_flow(self, request: Request):
        request.headers["X-Service-ID"] = self.realm
        yield from super().auth_flow(request)
