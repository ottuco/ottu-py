import logging
import typing
from json import JSONDecodeError
from urllib.parse import urlparse

import httpx

from .mixins import ResponseMixin

logger = logging.getLogger("ottu-py")


class OttuPYResponse(ResponseMixin):
    ...


class BaseRequestResponseHandler:
    """Base class for shared functionality between sync and async handlers."""

    def __init__(
        self,
        session: typing.Union[httpx.Client, httpx.AsyncClient],
        method: str,
        url: str,
        **kwargs,
    ):
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

    def _log_request(self):
        logger.info(
            f"Sending {self.method} request to {self.url} with args {self.kwargs}",
        )

    def _log_response(self, response: OttuPYResponse):
        if response.success:
            logger.info(
                f"Received {response.status_code} response "
                f"from {self.url} with args {self.kwargs}",
            )
        else:
            logger.error(
                f"Received {response.status_code} response "
                f"from {self.url} with args {self.kwargs}. Error: {response.error}",
            )


class RequestResponseHandler(BaseRequestResponseHandler):
    """Synchronous request handler."""

    def __init__(self, session: httpx.Client, method: str, url: str, **kwargs):
        super().__init__(session, method, url, **kwargs)
        self.session: httpx.Client = session

    def _process(self) -> OttuPYResponse:
        try:
            self._log_request()
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
        response = self._process()
        self._log_response(response)
        return response


class AsyncRequestResponseHandler(BaseRequestResponseHandler):
    """Asynchronous request handler."""

    def __init__(self, session: httpx.AsyncClient, method: str, url: str, **kwargs):
        super().__init__(session, method, url, **kwargs)
        self.session: httpx.AsyncClient = session

    async def _process(self) -> OttuPYResponse:
        try:
            self._log_request()
            response = await self.session.request(
                method=self.method,
                url=self.url,
                **self.kwargs,
            )
            return self.process_response(response)
        except httpx.HTTPError as exc:
            return self.process_httpx_error(exc)
        except Exception as exc:
            return self.process_unknown_error(exc)

    async def process(self) -> OttuPYResponse:
        response = await self._process()
        self._log_response(response)
        return response
