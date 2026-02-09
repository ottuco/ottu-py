from __future__ import annotations

import httpx
from httpx import Auth

from . import urls
from .cards import Card
from .enums import HTTPMethod, TxnType
from .request import OttuPYResponse, RequestResponseHandler
from .session import Session
from .utils.helpers import remove_empty_values


class Ottu:
    _session: Session | None = None
    _card: Card | None = None
    default_timeout: int = 30
    session_cls: type[Session] = Session
    request_response_handler: type[RequestResponseHandler] = RequestResponseHandler

    def __init__(
        self,
        merchant_id: str,
        auth: Auth,
        customer_id: str | None = None,
        is_sandbox: bool = True,
        timeout: int | None = None,
    ) -> None:
        self.merchant_id = merchant_id
        self.host_url = f"https://{merchant_id}"
        self.auth = auth
        self.customer_id = customer_id
        self.is_sandbox = is_sandbox
        self.env_type = "sandbox" if is_sandbox else "production"
        self.timeout = timeout or self.default_timeout

        # Other initializations
        self.request_session = self.__create_session()

    def __create_session(self) -> httpx.Client:
        return httpx.Client(auth=self.auth)

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
            timeout=self.timeout,
            **request_params,
        ).process()

    # Core Methods

    @property
    def session(self):
        if self._session is None:
            self._session = self.session_cls(ottu=self)
        return self._session

    def _update_session(self, session: Session) -> None:
        self._session = session

    def checkout(
        self,
        *,
        txn_type: TxnType,
        amount: str,
        currency_code: str,
        pg_codes: list[str],
        payment_type: str = "one_off",
        customer_id: str | None = None,
        customer_email: str | None = None,
        customer_phone: str | None = None,
        customer_first_name: str | None = None,
        customer_last_name: str | None = None,
        agreement: dict | None = None,
        card_acceptance_criteria: dict | None = None,
        attachment: str | None = None,
        billing_address: dict | None = None,
        due_datetime: str | None = None,
        email_recipients: list[str] | None = None,
        expiration_time: str | None = None,
        extra: dict | None = None,
        generate_qr_code: bool | None = None,
        language: str | None = None,
        mode: str | None = None,
        notifications: dict | None = None,
        order_no: str | None = None,
        product_type: str | None = None,
        redirect_url: str | None = None,
        shopping_address: dict | None = None,
        shortify_attachment_url: bool | None = None,
        shortify_checkout_url: bool | None = None,
        vendor_name: str | None = None,
        webhook_url: str | None = None,
        include_sdk_setup_preload: bool | None = None,
        **kwargs,
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
            include_sdk_setup_preload=include_sdk_setup_preload,
            **kwargs,
        )

    def auto_debit(
        self,
        token: str,
        session_id: str,
    ):
        return self.session.auto_debit(token=token, session_id=session_id)

    @property
    def cards(self) -> Card:
        if self._card is None:
            self._card = Card(ottu=self)
        return self._card

    def checkout_autoflow(
        self,
        *,
        txn_type: TxnType,
        amount: str,
        currency_code: str,
        payment_type: str = "one_off",
        customer_id: str | None = None,
        customer_email: str | None = None,
        customer_phone: str | None = None,
        customer_first_name: str | None = None,
        customer_last_name: str | None = None,
        agreement: dict | None = None,
        card_acceptance_criteria: dict | None = None,
        attachment: str | None = None,
        billing_address: dict | None = None,
        due_datetime: str | None = None,
        email_recipients: list[str] | None = None,
        expiration_time: str | None = None,
        extra: dict | None = None,
        generate_qr_code: bool | None = None,
        language: str | None = None,
        mode: str | None = None,
        notifications: dict | None = None,
        order_no: str | None = None,
        product_type: str | None = None,
        redirect_url: str | None = None,
        shopping_address: dict | None = None,
        shortify_attachment_url: bool | None = None,
        shortify_checkout_url: bool | None = None,
        vendor_name: str | None = None,
        webhook_url: str | None = None,
        include_sdk_setup_preload: bool | None = None,
        checkout_extra_args: dict | None = None,
    ):
        return self.session.checkout_autoflow(
            txn_type=txn_type,
            amount=amount,
            currency_code=currency_code,
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
            include_sdk_setup_preload=include_sdk_setup_preload,
            checkout_extra_args=checkout_extra_args,
        )

    def auto_debit_autoflow(
        self,
        *,
        txn_type: TxnType,
        amount: str,
        currency_code: str,
        customer_id: str,
        agreement: dict,
        pg_codes: list[str] | None = None,
        customer_email: str | None = None,
        customer_phone: str | None = None,
        customer_first_name: str | None = None,
        customer_last_name: str | None = None,
        card_acceptance_criteria: dict | None = None,
        attachment: str | None = None,
        billing_address: dict | None = None,
        due_datetime: str | None = None,
        email_recipients: list[str] | None = None,
        expiration_time: str | None = None,
        extra: dict | None = None,
        generate_qr_code: bool | None = None,
        language: str | None = None,
        mode: str | None = None,
        notifications: dict | None = None,
        order_no: str | None = None,
        product_type: str | None = None,
        redirect_url: str | None = None,
        shopping_address: dict | None = None,
        shortify_attachment_url: bool | None = None,
        shortify_checkout_url: bool | None = None,
        vendor_name: str | None = None,
        webhook_url: str | None = None,
        include_sdk_setup_preload: bool | None = None,
        checkout_extra_args: dict | None = None,
        token: str | None = None,
    ):
        return self.session.auto_debit_autoflow(
            txn_type=txn_type,
            amount=amount,
            currency_code=currency_code,
            customer_id=customer_id,
            pg_codes=pg_codes,
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
            include_sdk_setup_preload=include_sdk_setup_preload,
            checkout_extra_args=checkout_extra_args,
            token=token,
        )

    def raw(
        self,
        method: str,
        path: str,
        headers: dict | None = None,
        **kwargs,
    ):
        """
        To send any sort of http requests to the server.
            method: str - HTTP method name.
                Eg: GET, POST, PUT, DELETE, etc.
            path: str - The path of the request.
                Eg: /b/api/v1/dashboard/statistics
            headers: dict - Optional headers to be sent with the request.
            kwargs: dict - Optional parameters to be sent with the request.
                Supports all the parameters that `httpx.Client.send` supports.
        """
        return self.send_request(
            path=path,
            method=method,
            headers=headers,
            **kwargs,
        )

    def get_payment_methods(
        self,
        plugin: str | TxnType,
        currencies: list[str] | None = None,
        customer_id: str | None = None,
        operation: str | None = None,
        tokenizable: bool = False,
        pg_names: list[str] | None = None,
    ) -> dict:
        if isinstance(plugin, TxnType):
            plugin = plugin.value
        return self._get_payment_methods(
            plugin=plugin,
            currencies=currencies,
            customer_id=customer_id,
            operation=operation,
            tokenizable=tokenizable,
            pg_names=pg_names,
        ).as_dict()

    def _get_payment_methods(
        self,
        plugin,
        currencies: list[str] | None = None,
        customer_id: str | None = None,
        operation: str | None = None,
        tokenizable: bool = False,
        pg_names: list[str] | None = None,
    ) -> OttuPYResponse:
        payload = {
            "plugin": plugin,
            "currencies": currencies,
            "customer_id": customer_id,
            "operation": operation,
            "tokenizable": tokenizable,
            "pg_names": pg_names,
            "type": "sandbox" if self.is_sandbox else "production",
        }
        payload = remove_empty_values(payload)
        return self.send_request(
            path=urls.PAYMENT_METHODS,
            method=HTTPMethod.POST,
            json=payload,
        )

    def __repr__(self):
        return f"Ottu({self.merchant_id})"
