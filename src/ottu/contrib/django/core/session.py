from ....errors import APIInterruptError
from ....session import Session as _Session
from .. import conf
from ..models import Checkout


class Session(_Session):
    def create(self, *args, **kwargs):
        if conf.WEBHOOK_URL and not kwargs.get("webhook_url"):
            kwargs["webhook_url"] = conf.WEBHOOK_URL
        return super().create(*args, **kwargs)

    def get_token_from_db(self, agreement, customer_id) -> str:
        """
        Get the token from the database
        """
        instance = Checkout.objects.filter(
            customer_id=customer_id,
            agreement__id=agreement.get("id"),
        ).first()
        if instance:
            return instance.token
        raise APIInterruptError(
            success=False,
            status_code=400,
            endpoint="",
            response={},
            error={"detail": "Token not found in the database"},
        )
