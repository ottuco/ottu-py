class OttuBaseError(Exception):
    def __init__(self, msg: str, **extra):
        self.msg = msg

    def __str__(self):
        return self.msg

    def __repr__(self):
        return f"<{self.__class__.__name__}({self.msg})>"


class ConfigurationError(OttuBaseError):
    ...


class ValidationError(OttuBaseError):
    ...


class UpstreamBase(OttuBaseError):
    def __init__(self, msg: str, status_code: int, **extra):
        self.status_code = status_code
        super().__init__(msg, **extra)


class UpstreamError(UpstreamBase):
    ...


class WebhookProcessingError(OttuBaseError):
    ...
