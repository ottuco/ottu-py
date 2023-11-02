from ....session import Session as _Session
from .. import conf


class Session(_Session):
    def create(self, *args, **kwargs):
        if conf.WEBHOOK_URL and not kwargs.get("webhook_url"):
            kwargs["webhook_url"] = conf.WEBHOOK_URL
        return super().create(*args, **kwargs)
