import httpx
from httpx import Auth, BasicAuth as _BasicAuth, Request


class BasicAuth(_BasicAuth):
    ...


class APIKeyAuth(Auth):
    def __init__(self, api_key: str):
        self.api_key = api_key

    def auth_flow(self, request: Request):
        request.headers["Authorization"] = f"Api-Key {self.api_key}"
        yield request


class KeyCloakAuth(Auth):
    def __init__(
        self,
        username: str,
        password: str,
        keycloak_host: str,
        realm: str,
        client_id: str = "frontend",
    ):
        self.username = username
        self.password = password
        self.keycloak_host = keycloak_host
        self.realm = realm
        self.client_id = client_id
        self._url = f"{self.keycloak_host}/auth/realms/{self.realm}/protocol/openid-connect/token"

    def get_access_token(self):
        response = httpx.post(
            url=self._url,
            data={
                "grant_type": "password",
                "client_id": self.client_id,
                "username": self.username,
                "password": self.password,
            },
        )
        return response.json()["access_token"]

    def auth_flow(self, request: Request):
        access_token = self.get_access_token()
        request.headers["Authorization"] = f"Bearer {access_token}"
        yield request
