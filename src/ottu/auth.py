from httpx import Auth, BasicAuth as _BasicAuth, Request


class BasicAuth(_BasicAuth):
    ...


class APIKeyAuth(Auth):
    def __init__(self, api_key: str):
        self.api_key = api_key

    def auth_flow(self, request: Request):
        request.headers["Authorization"] = f"Api-Key {self.api_key}"
        yield request
