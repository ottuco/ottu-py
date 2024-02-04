import typing

import httpx
from httpx import Auth, BasicAuth as _BasicAuth, Request


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


class APIKeyAuth(Auth):
    def __init__(self, api_key: str):
        self.api_key = api_key

    def auth_flow(self, request: Request):
        request.headers["Authorization"] = f"Api-Key {self.api_key}"
        yield request

    def __bool__(self):
        return bool(self.api_key)


class KeycloakAuthBase:
    grant_type: str

    def __init__(self, host: str, realm: str, *args, **kwargs):
        self.host = host
        self.realm = realm

    @property
    def token_url(self) -> str:
        return (
            f"https://{self.host}/auth/realms/"
            f"{self.realm}/protocol/openid-connect/token"
        )

    def get_token_request_payload(self) -> dict:
        return {"grant_type": self.grant_type}

    def get_token(self) -> str:
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        data = self.get_token_request_payload()
        response = httpx.post(url=self.token_url, data=data, headers=headers)
        response.raise_for_status()
        return response.json().get("access_token")

    def auth_flow(self, request: Request):
        access_token = self.get_token()
        request.headers["Authorization"] = f"Bearer {access_token}"
        request.headers["X-Service-ID"] = self.realm
        yield request


class KeycloakPasswordAuth(KeycloakAuthBase, Auth):
    grant_type = "password"

    def __init__(
        self,
        username: str,
        password: str,
        client_id: str,
        *args,
        client_secret: typing.Optional[str] = None,
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
