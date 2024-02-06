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
