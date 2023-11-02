import base64
import typing

import httpx
from httpx import Auth

from . import urls
from .cards import Card
from .enums import HTTPMethod, TxnType
from .errors import ConfigurationError
from .request import OttuPYResponse, RequestResponseHandler
from .session import Session
from .utils import remove_empty_values


class Ottu:
    _session: typing.Optional[Session] = None
    _card: typing.Optional[Card] = None
    session_cls: typing.Type[Session] = Session
    request_response_handler: typing.Type[
        RequestResponseHandler
    ] = RequestResponseHandler

    def __init__(
        self,
        merchant_id: str,
        auth: Auth,
        customer_id: typing.Optional[str] = None,
    ) -> None:
        self.host_url = f"https://{merchant_id}"
        self.auth = auth
        self.customer_id = customer_id

        # Validations
        self.__validate_init()

        # Other initializations
        self.request_session = self.__create_session()

    def __create_session(self) -> httpx.Client:
        return httpx.Client(auth=self.auth)

    def __validate_init(self) -> None:
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

    # Handle requests

    def send_request(
        self,
        path: str,
        method: str,
        **request_params,
    ) -> OttuPYResponse:
        return self.request_response_handler(
            session=self.request_session,
            method=method,
            url=f"{self.host_url}{path}",
            **request_params,
        ).process()

    # Core Methods

    @property
    def session(self):
        if self._session is None:
            self._session = self.session_cls(ottu=self)
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

    def auto_debit_checkout(
        self,
        txn_type: TxnType,
        amount: str,
        currency_code: str,
        pg_codes: list[str],
        agreement: dict,
        customer_id: typing.Optional[str] = None,
        customer_email: typing.Optional[str] = None,
        customer_phone: typing.Optional[str] = None,
        customer_first_name: typing.Optional[str] = None,
        customer_last_name: typing.Optional[str] = None,
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
    ):
        return self.session.auto_debit_checkout(
            txn_type=txn_type,
            amount=amount,
            currency_code=currency_code,
            pg_codes=pg_codes,
            agreement=agreement,
            customer_id=customer_id,
            customer_email=customer_email,
            customer_phone=customer_phone,
            customer_first_name=customer_first_name,
            customer_last_name=customer_last_name,
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

    def auto_debit(
        self,
        token: str,
        session_id: str,
    ):
        return self.session.auto_debit(token=token, session_id=session_id)

    def auto_flow(
        self,
        txn_type: TxnType,
        amount: str,
        currency_code: str,
        agreement: dict,
        is_sandbox: bool,
        customer_id: typing.Optional[str] = None,
        customer_email: typing.Optional[str] = None,
        customer_phone: typing.Optional[str] = None,
        customer_first_name: typing.Optional[str] = None,
        customer_last_name: typing.Optional[str] = None,
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
    ):
        pg_info = self._get_auto_debit_pg_info(txn_type=txn_type)
        pg_codes = self._get_auto_debit_pg_codes(pg_info)
        if len(pg_codes) == 0:
            return OttuPYResponse(
                success=False,
                status_code=400,
                endpoint=urls.PAYMENT_METHODS,
                response={},
                error={"detail": "No payment gateways found for auto debit"},
            ).as_dict()
        if len(pg_codes) > 1:
            return OttuPYResponse(
                success=False,
                status_code=400,
                endpoint=urls.PAYMENT_METHODS,
                response={},
                error={"detail": "More than one payment gateway found for auto debit"},
            ).as_dict()
        card_type = "sandbox" if is_sandbox else "production"
        tokens = self._get_auto_debit_card_token(
            pg_codes=pg_codes,
            card_type=card_type,
            agreement_id=agreement.get("id", ""),
        )
        if len(tokens) == 0:
            return OttuPYResponse(
                success=False,
                status_code=400,
                endpoint=urls.USER_CARDS,
                response={},
                error={"detail": "No cards found for auto debit"},
            ).as_dict()
        if len(tokens) > 1:
            return OttuPYResponse(
                success=False,
                status_code=400,
                endpoint=urls.USER_CARDS,
                response={},
                error={"detail": "More than one card found for auto debit"},
            ).as_dict()
        token = tokens[0]
        response = self.auto_debit_checkout(
            txn_type=txn_type,
            amount=amount,
            currency_code=currency_code,
            pg_codes=pg_codes,
            agreement=agreement,
            customer_id=customer_id,
            customer_email=customer_email,
            customer_phone=customer_phone,
            customer_first_name=customer_first_name,
            customer_last_name=customer_last_name,
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
        if not response.get("success", False):
            return response
        return self.auto_debit(token=token, session_id=self.session.session_id)

    def _get_auto_debit_card_token(
        self,
        pg_codes: list[str],
        card_type: str,
        agreement_id: str,
    ) -> list[str]:
        response = self.cards.list(
            pg_codes=pg_codes,
            type=card_type,
            agreement_id=agreement_id,
        )
        card_info = response.get("response", [])
        return [card["token"] for card in card_info if card["is_expired"] is False]

    def _get_auto_debit_pg_info(self, txn_type: TxnType) -> list:
        pg_info = self.get_payment_methods(plugin=txn_type.value, tokenizable=True)
        return pg_info.get("response", {}).get("payment_methods", [])

    def _get_auto_debit_pg_codes(self, pg_info: list) -> list[str]:
        return [pg["code"] for pg in pg_info]

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
            path=urls.PAYMENT_METHODS,
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
