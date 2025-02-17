import typing

import httpx
from httpx import Auth

from . import urls
from .cards import Card
from .enums import HTTPMethod, TxnType
from .request import OttuPYResponse, RequestResponseHandler
from .session import Session
from .utils.helpers import remove_empty_values


class Ottu:
    _session: typing.Optional[Session] = None
    _card: typing.Optional[Card] = None
    default_timeout: int = 30
    session_cls: typing.Type[Session] = Session
    request_response_handler: typing.Type[
        RequestResponseHandler
    ] = RequestResponseHandler

    def __init__(
        self,
        merchant_id: str,
        auth: Auth,
        customer_id: typing.Optional[str] = None,
        is_sandbox: bool = True,
        timeout: typing.Optional[int] = None,
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
        include_sdk_setup_preload: typing.Optional[bool] = None,
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
        include_sdk_setup_preload: typing.Optional[bool] = None,
        checkout_extra_args: typing.Optional[dict] = None,
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
        pg_codes: typing.Optional[list[str]] = None,
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
        include_sdk_setup_preload: typing.Optional[bool] = None,
        checkout_extra_args: typing.Optional[dict] = None,
        token: typing.Optional[str] = None,
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
        headers: typing.Optional[dict] = None,
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
        plugin,
        currencies: typing.Optional[list[str]] = None,
        customer_id: typing.Optional[str] = None,
        operation: typing.Optional[str] = None,
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

    def _get_payment_methods(
        self,
        plugin,
        currencies: typing.Optional[list[str]] = None,
        customer_id: typing.Optional[str] = None,
        operation: typing.Optional[str] = None,
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
