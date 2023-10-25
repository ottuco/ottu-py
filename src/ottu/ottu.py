import base64
import typing

import httpx

from .cards import Card
from .enums import HTTPMethod, TxnType
from .errors import ConfigurationError
from .request import OttuPYResponse, RequestResponseHandler
from .session import Session
from .utils import remove_empty_values


class Ottu:
    _session: typing.Optional[Session] = None
    _card: typing.Optional[Card] = None
    url_payment_methods = "/b/pbl/v2/payment-methods/"

    def __init__(
        self,
        merchant_id: str,
        username: typing.Optional[str] = None,
        password: typing.Optional[str] = None,
        api_key: typing.Optional[str] = None,
        customer_id: typing.Optional[str] = None,
    ) -> None:
        self.host_url = f"https://{merchant_id}"
        self.username = username
        self.password = password
        self.api_key = api_key
        self.customer_id = customer_id

        # Validations
        self.__validate_init()

        # Other initializations
        self.request_session = self.__create_session()

    def __generate_auth_header(self) -> typing.Dict[str, str]:
        if self.api_key:
            value = f"Api-Key {self.api_key}"
        else:
            creds = base64.b64encode(
                f"{self.username}:{self.password}".encode(),
            ).decode("utf-8")
            value = f"Basic {creds}"
        return {"Authorization": value}

    def __create_session(self) -> httpx.Client:
        headers = {
            **self.__generate_auth_header(),
        }
        return httpx.Client(headers=headers)

    def __validate_init(self) -> None:
        self.__validate_auth_params()
        self.__validate_host_url()

    def __validate_host_url(self) -> None:
        """
        Validates host URL. URL must be
        1. https
        2. not end with /
        3. must contain domain name with protocol
            Example:
                1. https://example.com - Correct
                2. https://example.com/ - Incorrect
                3. https://example.com/anypath - Incorrect

        """
        msg_example = (
            "Example: `https://example.com`, "
            "but not `https://example.com/` or "
            "`https://example.com/anypath`"
        )
        if not self.host_url.startswith("https://"):
            msg = f"Host URL must start with https://. {msg_example}"
            raise ConfigurationError(msg)
        if self.host_url.endswith("/"):
            msg = f"Host URL must not end with /. {msg_example}"
            raise ConfigurationError(msg)
        if self.host_url.count("/") != 2:
            msg = f"Host URL must contain domain name with protocol. {msg_example}"
            raise ConfigurationError(msg)

    def __validate_auth_params(self) -> None:
        if self.api_key:
            # Authentication using API key, we don't need username and password
            if self.username or self.password:
                msg = (
                    "You are using API key for authentication, "
                    "username and password are not required"
                )
                raise ConfigurationError(msg)
        elif self.username and self.password:
            # Authentication using username and password, we don't need API key
            if self.api_key:
                msg = (
                    "You are using username and password "
                    "for authentication, API key is not required"
                )
                raise ConfigurationError(msg)
        else:
            msg = (
                "You must provide either API key or "
                "username and password for authentication"
            )
            raise ConfigurationError(msg)

    # Handle requests
    def send_request(
        self,
        path: str,
        method: str,
        **request_params,
    ) -> OttuPYResponse:
        return RequestResponseHandler(
            session=self.request_session,
            method=method,
            url=f"{self.host_url}{path}",
            **request_params,
        ).process()

    # Core Methods

    @property
    def session(self):
        if self._session is None:
            self._session = Session(ottu=self)
        return self._session

    def _update_session(self, session: Session):
        self._session = session

    def checkout(
        self,
        txn_type: TxnType,
        amount: str,
        currency_code: str,
        pg_codes: list[str],
        payment_type: str = "one_off",
        customer_id: typing.Optional[str] = None,
        customer_email: typing.Optional[str] = None,
        customer_phone: typing.Optional[str] = None,
        customer_first_name: typing.Optional[str] = None,
        customer_last_name: typing.Optional[str] = None,
        agreement: typing.Optional[dict] = None,
        card_acceptance_criteria: typing.Optional[dict] = None,
        attachment: typing.Optional[str] = None,
        billing_address: typing.Optional[dict] = None,
        due_datetime: typing.Optional[str] = None,
        email_recipients: typing.Optional[list[str]] = None,
        expiration_time: typing.Optional[str] = None,
        extra: typing.Optional[dict] = None,
        generate_qr_code: typing.Optional[bool] = None,
        language: typing.Optional[str] = None,
        mode: typing.Optional[str] = None,
        notifications: typing.Optional[dict] = None,
        order_no: typing.Optional[str] = None,
        product_type: typing.Optional[str] = None,
        redirect_url: typing.Optional[str] = None,
        shopping_address: typing.Optional[dict] = None,
        shortify_attachment_url: typing.Optional[bool] = None,
        shortify_checkout_url: typing.Optional[bool] = None,
        vendor_name: typing.Optional[str] = None,
        webhook_url: typing.Optional[str] = None,
    ) -> dict:
        """
        a proxy method to `Session.create(...)`
        """
        return self.session.create(
            txn_type=txn_type,
            amount=amount,
            currency_code=currency_code,
            pg_codes=pg_codes,
            payment_type=payment_type,
            customer_id=customer_id,
            customer_email=customer_email,
            customer_phone=customer_phone,
            customer_first_name=customer_first_name,
            customer_last_name=customer_last_name,
            agreement=agreement,
            card_acceptance_criteria=card_acceptance_criteria,
            attachment=attachment,
            billing_address=billing_address,
            due_datetime=due_datetime,
            email_recipients=email_recipients,
            expiration_time=expiration_time,
            extra=extra,
            generate_qr_code=generate_qr_code,
            language=language,
            mode=mode,
            notifications=notifications,
            order_no=order_no,
            product_type=product_type,
            redirect_url=redirect_url,
            shopping_address=shopping_address,
            shortify_attachment_url=shortify_attachment_url,
            shortify_checkout_url=shortify_checkout_url,
            vendor_name=vendor_name,
            webhook_url=webhook_url,
        )

    @property
    def cards(self) -> Card:
        if self._card is None:
            self._card = Card(ottu=self)
        return self._card

    def _get_payment_methods(
        self,
        plugin,
        currencies: typing.Optional[list[str]] = None,
        customer_id: typing.Optional[str] = None,
        operation: str = "purchase",
        tokenizable: bool = False,
        pg_names: typing.Optional[list[str]] = None,
    ) -> OttuPYResponse:
        payload = {
            "plugin": plugin,
            "currencies": currencies,
            "customer_id": customer_id,
            "operation": operation,
            "tokenizable": tokenizable,
            "pg_names": pg_names,
        }
        payload = remove_empty_values(payload)
        return self.send_request(
            path=self.url_payment_methods,
            method=HTTPMethod.POST,
            json=payload,
        )

    def get_payment_methods(
        self,
        plugin,
        currencies: typing.Optional[list[str]] = None,
        customer_id: typing.Optional[str] = None,
        operation: str = "purchase",
        tokenizable: bool = False,
        pg_names: typing.Optional[list[str]] = None,
    ) -> dict:
        return self._get_payment_methods(
            plugin=plugin,
            currencies=currencies,
            customer_id=customer_id,
            operation=operation,
            tokenizable=tokenizable,
            pg_names=pg_names,
        ).as_dict()
