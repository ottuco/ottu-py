from .mixins import ResponseMixin


class OttuBaseError(Exception):
    def __init__(self, msg: str, **extra):
        self.msg = msg

    def __str__(self):
        return self.msg

    def __repr__(self):
        return f"<{self.__class__.__name__}({self.msg})>"


class APIInterruptError(ResponseMixin, OttuBaseError):
    def __str__(self):
        return str(self.error)


class ConfigurationError(OttuBaseError):
    ...


class ValidationError(OttuBaseError):
    ...


class WebhookProcessingError(OttuBaseError):
    ...
