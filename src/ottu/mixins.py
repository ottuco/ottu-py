from __future__ import annotations

from typing import Any

from .utils.dataclasses import dynamic_asdict


class ResponseMixin:
    def __init__(
        self,
        success: bool,
        status_code: int,
        endpoint: str,
        response: dict[str, Any],
        error: dict[str, Any],
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


class AsDictMixin:
    def as_dict(self) -> dict:
        return dynamic_asdict(self)  # type: ignore
