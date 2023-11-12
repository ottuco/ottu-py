from json import JSONDecodeError
from urllib.parse import urlparse

import httpx


class OttuPYResponse:
    def __init__(
        self,
        success: bool,
        status_code: int,
        endpoint: str,
        response: dict,
        error: dict,
    ):
        self.success = success
        self.status_code = status_code
        self.endpoint = endpoint
        self.response = response
        self.error = error

    def as_dict(self) -> dict:
        return {
            "success": self.success,
            "status_code": self.status_code,
            "endpoint": self.endpoint,
            "response": self.response,
            "error": self.error,
        }


class RequestResponseHandler:
    def __init__(self, session: httpx.Client, method: str, url: str, **kwargs):
        self.session = session
        self.method = method
        self.url = url
        self.kwargs = kwargs

    @property
    def path(self) -> str:
        """
        The path of the request.
        """
        return urlparse(self.url).path

    def _process_response(self, response: httpx.Response) -> dict:
        if response.status_code == 204:
            return {}

        try:
            result = response.json()
        except JSONDecodeError:
            result = {"detail": response.text}
        return result

    def parse_success_response(
        self,
        httpx_response: httpx.Response,
        parsed_response: dict,
    ) -> OttuPYResponse:
        return OttuPYResponse(
            success=True,
            status_code=httpx_response.status_code,
            endpoint=self.path,
            response=parsed_response,
            error={},
        )

    def parse_non_2xx_error_response(
        self,
        httpx_response: httpx.Response,
        parsed_response: dict,
    ) -> OttuPYResponse:
        return OttuPYResponse(
            success=False,
            status_code=httpx_response.status_code,
            endpoint=self.path,
            response={},
            error=parsed_response,
        )

    def process_response(self, response: httpx.Response) -> OttuPYResponse:
        parsed_response = self._process_response(response)
        if 200 <= response.status_code <= 299:
            return self.parse_success_response(
                httpx_response=response,
                parsed_response=parsed_response,
            )
        return self.parse_non_2xx_error_response(
            httpx_response=response,
            parsed_response=parsed_response,
        )

    def process_unknown_error(self, exc: Exception) -> OttuPYResponse:
        return self._parse_error(exc)

    def process_httpx_error(self, exc: httpx.HTTPError) -> OttuPYResponse:
        return self._parse_error(exc)

    def _parse_error(self, exc: Exception) -> OttuPYResponse:
        return OttuPYResponse(
            success=False,
            status_code=500,
            endpoint=self.path,
            response={},
            error={"detail": str(exc)},
        )

    def _process(self) -> OttuPYResponse:
        try:
            response = self.session.request(
                method=self.method,
                url=self.url,
                **self.kwargs,
            )
            return self.process_response(response)
        except httpx.HTTPError as exc:
            return self.process_httpx_error(exc)
        except Exception as exc:
            return self.process_unknown_error(exc)

    def process(self) -> OttuPYResponse:
        return self._process()
