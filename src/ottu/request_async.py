import logging
from json import JSONDecodeError
from urllib.parse import urlparse

import httpx

from .mixins import ResponseMixin
from .request import OttuPYResponse, RequestResponseHandler

logger = logging.getLogger("ottu-py")


class AsyncRequestResponseHandler(RequestResponseHandler):
    def __init__(self, session: httpx.AsyncClient, method: str, url: str, **kwargs):
        super().__init__(session=session, method=method, url=url, **kwargs)

    async def _process(self) -> OttuPYResponse:
        try:
            logger.info(
                f"Sending {self.method} request to {self.url} with args {self.kwargs}"
            )
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
        if response.success:
            logger.info(
                f"Received {response.status_code} response "
                f"from {self.url} with args {self.kwargs}"
            )
        else:
            logger.error(
                f"Received {response.status_code} response "
                f"from {self.url} with args {self.kwargs}. Error: {response.error}"
            )
        return response
