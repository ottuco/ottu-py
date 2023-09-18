import typing

from pydantic import BaseModel

from .enums import HTTPMethod, TxnType

if typing.TYPE_CHECKING:
    from .ottu import Ottu

from .errors import ValidationError


class Session(BaseModel):
    amount: typing.Optional[str] = None
    checkout_url: typing.Optional[str] = None
    currency_code: typing.Optional[str] = None
    customer_id: typing.Optional[str] = None
    due_datetime: typing.Optional[str] = None
    expiration_time: typing.Optional[str] = None
    initiator_id: typing.Optional[int] = None
    language: typing.Optional[str] = None
    mode: typing.Optional[str] = None
    operation: typing.Optional[str] = None
    payment_methods: typing.Optional[list[dict]] = None
    pg_codes: typing.Optional[list[str]] = None
    state: typing.Optional[str] = None
    session_id: typing.Optional[str] = None
    type: typing.Optional[str] = None

    def __init__(self, ottu: "Ottu", **data):
        super().__init__(**data)
        self._ottu = ottu

    def __str__(self):
        return f"Session({self.session_id or '######'})"

    def __repr__(self):
        return str(self)

    def update(self, **kwargs):
        handler = SessionHandler(self._ottu)
        return handler.update_session(
            session_id=self.session_id,
            **kwargs,
        )


class SessionHandler:
    """
    Creates a new checkout session.
    """

    path = "/b/checkout/v1/pymt-txn/"

    def __init__(self, ottu: "Ottu"):
        self.ottu = ottu

    def __validate_customer_id(self, customer_id: typing.Optional[str] = None) -> None:
        if self.ottu.customer_id or customer_id:
            return
        raise ValidationError("`customer_id` is required")

    def checkout(
        self,
        txn_type: TxnType,
        amount: str,
        currency_code: str,
        pg_codes: list[str],
        customer_id: typing.Optional[str] = None,
        customer_first_name: typing.Optional[str] = None,
        customer_last_name: typing.Optional[str] = None,
    ) -> Session:
        """
        Creates a new checkout session.
        :param txn_type: Transaction type
        :param amount: Amount to be paid
        :param currency_code: Currency code
        :param pg_codes: Payment gateway codes
        :param customer_id: Customer ID
        :param customer_first_name: Customer first name
        :param customer_last_name: Customer last name
        :return:
        """
        self.__validate_customer_id(customer_id)
        customer_id = customer_id or self.ottu.customer_id
        payload = {
            "type": txn_type.value,
            "amount": amount,
            "currency_code": currency_code,
            "pg_codes": pg_codes,
            "customer_id": customer_id,
        }
        if customer_first_name:
            payload["customer_first_name"] = customer_first_name
        if customer_last_name:
            payload["customer_last_name"] = customer_last_name
        response = self.ottu.send_request(
            path=self.path,
            method=HTTPMethod.POST,
            json=payload,
        )
        return Session(
            ottu=self.ottu,
            **response.json(),
        )

    def update_session(
        self,
        session_id: str,
        txn_type: typing.Optional[TxnType] = None,
        amount: typing.Optional[str] = None,
        currency_code: typing.Optional[str] = None,
        pg_codes: typing.Optional[list[str]] = None,
        customer_id: typing.Optional[str] = None,
        customer_first_name: typing.Optional[str] = None,
        customer_last_name: typing.Optional[str] = None,
    ):
        self.__validate_customer_id(customer_id)
        payload: dict[str, typing.Union[str, list]] = {}
        if txn_type:
            payload["type"] = txn_type.value
        if amount:
            payload["amount"] = amount
        if currency_code:
            payload["currency_code"] = currency_code
        if pg_codes:
            payload["pg_codes"] = pg_codes
        if customer_id:
            payload["customer_id"] = customer_id
        if customer_first_name:
            payload["customer_first_name"] = customer_first_name
        if customer_last_name:
            payload["customer_last_name"] = customer_last_name

        response = self.ottu.send_request(
            path=f"{self.path}{session_id}",
            method=HTTPMethod.PATCH,
            json=payload,
        )
        return Session(ottu=self.ottu, **response.json())
