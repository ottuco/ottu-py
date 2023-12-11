import typing
from dataclasses import dataclass

from . import urls
from .decorators import interruption_handler
from .enums import HTTPMethod, TxnType
from .errors import APIInterruptError, ValidationError
from .mixins import AsDictMixin
from .request import OttuPYResponse
from .utils import remove_empty_values

if typing.TYPE_CHECKING:
    from .ottu import Ottu


@dataclass
class PaymentMethod(AsDictMixin):
    code: typing.Optional[str] = None
    name: typing.Optional[str] = None
    pg: typing.Optional[str] = None
    type: typing.Optional[str] = None
    amount: typing.Optional[str] = None
    currency_code: typing.Optional[str] = None
    fee: typing.Optional[str] = None
    fee_description: typing.Optional[str] = None
    icon: typing.Optional[str] = None
    flow: typing.Optional[str] = None
    redirect_url: typing.Optional[str] = None

    def __str__(self):
        return f"PaymentMethod({self.code or '######'})"

    def __repr__(self):
        return str(self)


class Session:
    url_session_create = "/b/checkout/v1/pymt-txn/"
    url_ops = "/b/pbl/v2/operation/"
    url_auto_debit = "/b/pbl/v2/auto-debit/"

    amount: typing.Optional[str] = None
    attachment: typing.Optional[str] = None
    attachment_short_url: typing.Optional[str] = None
    billing_address: typing.Optional[dict] = None
    checkout_short_url: typing.Optional[str] = None
    checkout_url: typing.Optional[str] = None
    currency_code: typing.Optional[str] = None
    customer_email: typing.Optional[str] = None
    customer_first_name: typing.Optional[str] = None
    customer_last_name: typing.Optional[str] = None
    customer_id: typing.Optional[str] = None
    customer_phone: typing.Optional[str] = None
    due_datetime: typing.Optional[str] = None
    email_recipients: typing.Optional[list[str]] = None
    expiration_time: typing.Optional[str] = None
    extra: typing.Optional[dict] = None
    initiator_id: typing.Optional[int] = None
    language: typing.Optional[str] = None
    mode: typing.Optional[str] = None
    notifications: typing.Optional[dict] = None
    operation: typing.Optional[str] = None
    order_no: typing.Optional[str] = None
    payment_methods: typing.Optional[list[PaymentMethod]] = None
    pg_codes: typing.Optional[list[str]] = None
    qr_code_url: typing.Optional[str] = None
    redirect_url: typing.Optional[str] = None
    session_id: typing.Optional[str] = None
    shipping_address: typing.Optional[dict] = None
    state: typing.Optional[str] = None
    type: typing.Optional[str] = None
    vendor_name: typing.Optional[str] = None
    webhook_url: typing.Optional[str] = None

    def __init__(self, ottu: "Ottu", **data):
        self.ottu = ottu
        for field, value in data.items():
            setattr(self, field, value)

        payment_methods = getattr(self, "payment_methods", [])
        if payment_methods:
            self.payment_methods = [
                PaymentMethod(
                    **payment_method,
                )
                for payment_method in payment_methods
            ]

    def __str__(self):
        return f"Session({self.session_id or '######'})"

    def __repr__(self):
        return str(self)

    def __bool__(self):
        return bool(self.session_id)

    def as_dict(self):
        fields = [
            "amount",
            "attachment",
            "attachment_short_url",
            "billing_address",
            "checkout_short_url",
            "checkout_url",
            "currency_code",
            "customer_email",
            "customer_first_name",
            "customer_last_name",
            "customer_id",
            "customer_phone",
            "due_datetime",
            "email_recipients",
            "expiration_time",
            "extra",
            "initiator_id",
            "language",
            "mode",
            "notifications",
            "operation",
            "order_no",
            "payment_methods",
            "pg_codes",
            "qr_code_url",
            "redirect_url",
            "session_id",
            "shipping_address",
            "state",
            "type",
            "vendor_name",
            "webhook_url",
        ]
        return remove_empty_values(
            {field: getattr(self, field, "") for field in fields},
        )

    def __validate_customer_id(self, customer_id: typing.Optional[str] = None) -> None:
        if self.customer_id or customer_id:
            return
        raise ValidationError("`customer_id` is required")

    def __path_to_file(self, path: str) -> typing.Tuple[str, bytes]:
        with open(path, "rb") as f:
            content = f.read()
            name = f.name or "attachment.pdf"
        return name, content

    def create(
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
        Creates a new checkout session.
        :param txn_type: Transaction type
        :param amount: Amount
        :param currency_code: Currency code
        :param pg_codes: Payment gateway codes
        :param customer_id: Customer ID
        :param customer_email: Customer email
        :param customer_phone: Customer phone
        :param customer_first_name: Customer first name
        :param customer_last_name: Customer last name
        :param agreement: Agreement
        :param card_acceptance_criteria: Card acceptance criteria
        :param attachment: Path to attachment
        :param billing_address: Billing address
        :param due_datetime: Due datetime
        :param email_recipients: Email recipients
        :param expiration_time: Expiration time
        :param extra: Extra
        :param generate_qr_code: Generate QR code
        :param language: Language
        :param mode: Mode
        :param notifications: Notifications
        :param order_no: Order number
        :param product_type: Product type
        :param redirect_url: Redirect URL
        :param shopping_address: Shopping address
        :param shortify_attachment_url: Shortify attachment URL
        :param shortify_checkout_url: Shortify checkout URL
        :param vendor_name: Vendor name
        :param webhook_url: Webhook URL
        :return: Session
        """
        self.__validate_customer_id(customer_id)
        customer_id = customer_id or self.ottu.customer_id
        payload = {
            "type": txn_type.value,
            "amount": amount,
            "currency_code": currency_code,
            "pg_codes": pg_codes,
            "payment_type": payment_type,
            "customer_id": customer_id,
            "customer_email": customer_email,
            "customer_phone": customer_phone,
            "customer_first_name": customer_first_name,
            "customer_last_name": customer_last_name,
            "agreement": agreement,
            "card_acceptance_criteria": card_acceptance_criteria,
            "billing_address": billing_address,
            "due_datetime": due_datetime,
            "email_recipients": email_recipients,
            "expiration_time": expiration_time,
            "extra": extra,
            "generate_qr_code": generate_qr_code,
            "language": language,
            "mode": mode,
            "notifications": notifications,
            "order_no": order_no,
            "product_type": product_type,
            "redirect_url": redirect_url,
            "shopping_address": shopping_address,
            "shortify_attachment_url": shortify_attachment_url,
            "shortify_checkout_url": shortify_checkout_url,
            "vendor_name": vendor_name,
            "webhook_url": webhook_url,
        }
        payload = remove_empty_values(payload)
        if attachment:
            json_or_form = {
                "data": payload,
                "files": {"attachment": self.__path_to_file(path=attachment)},
            }
        else:
            json_or_form = {
                "json": payload,
            }
        ottu_py_response = self.ottu.send_request(
            path=self.url_session_create,
            method=HTTPMethod.POST,
            **json_or_form,
        )
        session = Session(
            ottu=self.ottu,
            **ottu_py_response.response,
        )
        if ottu_py_response.success:
            self.ottu._update_session(session)
        return ottu_py_response.as_dict()

    def retrieve(self, session_id: str) -> dict:
        """
        Retrieves a checkout session.
        :param session_id: Session ID
        """
        ottu_py_response = self.ottu.send_request(
            path=f"{self.url_session_create}{session_id}",
            method=HTTPMethod.GET,
        )
        session = Session(
            ottu=self.ottu,
            **ottu_py_response.response,
        )
        if ottu_py_response.success:
            self.ottu._update_session(session)
        return ottu_py_response.as_dict()

    def refresh(self, session_id: typing.Optional[str] = None) -> typing.Optional[dict]:
        """
        Reloads the payment attributes from upstream by calling the `retrieve` method.
        """
        session_id = session_id or self.session_id
        if session_id:
            response = self.retrieve(session_id=session_id)
            if response["success"]:
                return response
        return None

    def update(
        self,
        amount: typing.Optional[str] = None,
        currency_code: typing.Optional[str] = None,
        pg_codes: typing.Optional[list[str]] = None,
        customer_id: typing.Optional[str] = None,
        customer_email: typing.Optional[str] = None,
        customer_phone: typing.Optional[str] = None,
        customer_first_name: typing.Optional[str] = None,
        customer_last_name: typing.Optional[str] = None,
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
        self.__validate_customer_id(customer_id)
        payload = {
            "amount": amount,
            "currency_code": currency_code,
            "pg_codes": pg_codes,
            "customer_id": customer_id,
            "customer_email": customer_email,
            "customer_phone": customer_phone,
            "customer_first_name": customer_first_name,
            "customer_last_name": customer_last_name,
            "billing_address": billing_address,
            "due_datetime": due_datetime,
            "email_recipients": email_recipients,
            "expiration_time": expiration_time,
            "extra": extra,
            "generate_qr_code": generate_qr_code,
            "language": language,
            "mode": mode,
            "notifications": notifications,
            "order_no": order_no,
            "product_type": product_type,
            "redirect_url": redirect_url,
            "shopping_address": shopping_address,
            "shortify_attachment_url": shortify_attachment_url,
            "shortify_checkout_url": shortify_checkout_url,
            "vendor_name": vendor_name,
            "webhook_url": webhook_url,
        }
        payload = remove_empty_values(payload)
        if attachment:
            json_or_form = {
                "data": payload,
                "files": {"attachment": self.__path_to_file(path=attachment)},
            }
        else:
            json_or_form = {
                "json": payload,
            }
        ottu_py_response = self.ottu.send_request(
            path=f"{self.url_session_create}{self.session_id}",
            method=HTTPMethod.PATCH,
            **json_or_form,
        )
        session = Session(ottu=self.ottu, **ottu_py_response.response)
        if ottu_py_response.success:
            self.ottu._update_session(session)
        return ottu_py_response.as_dict()

    def auto_debit(self, token: str, session_id: str) -> dict:
        payload = {
            "session_id": session_id,
            "token": token,
        }
        ottu_py_response = self.ottu.send_request(
            path=self.url_auto_debit,
            method=HTTPMethod.POST,
            json=payload,
        )
        return ottu_py_response.as_dict()

    def ops(
        self,
        operation: str,
        order_id: typing.Optional[str] = None,
        session_id: typing.Optional[str] = None,
        amount: typing.Optional[str] = None,
        headers: typing.Optional[dict] = None,
    ) -> OttuPYResponse:
        if session_id is None:
            session_id = self.session_id

        if not session_id and not order_id:
            raise ValidationError("session_id or order_id is required")

        payload = {
            "session_id": session_id,
            "order_no": order_id,
            "operation": operation,
            "amount": amount,
        }
        payload = remove_empty_values(payload)
        return self.ottu.send_request(
            path=self.url_ops,
            method=HTTPMethod.POST,
            json=payload,
            headers=headers,
        )

    def cancel(
        self,
        order_id: typing.Optional[str] = None,
        session_id: typing.Optional[str] = None,
    ) -> dict:
        ottu_py_response = self.ops(
            operation="cancel",
            order_id=order_id,
            session_id=session_id,
        )
        if ottu_py_response.success:
            self.refresh()
        return ottu_py_response.as_dict()

    def expire(
        self,
        order_id: typing.Optional[str] = None,
        session_id: typing.Optional[str] = None,
    ) -> dict:
        ottu_py_response = self.ops(
            operation="expire",
            order_id=order_id,
            session_id=session_id,
        )
        if ottu_py_response.success:
            self.refresh()
        return ottu_py_response.as_dict()

    def delete(
        self,
        order_id: typing.Optional[str] = None,
        session_id: typing.Optional[str] = None,
    ) -> dict:
        ottu_py_response = self.ops(
            operation="delete",
            order_id=order_id,
            session_id=session_id,
        )
        return ottu_py_response.as_dict()

    def capture(
        self,
        order_id: typing.Optional[str] = None,
        session_id: typing.Optional[str] = None,
        amount: typing.Optional[str] = None,
        tracking_key: typing.Optional[str] = None,
    ) -> dict:
        headers = None
        if tracking_key:
            headers = {
                "Tracking-Key": tracking_key,
            }
        ottu_py_response = self.ops(
            operation="capture",
            order_id=order_id,
            session_id=session_id,
            amount=amount,
            headers=headers,
        )
        if ottu_py_response.success:
            self.refresh()
        return ottu_py_response.as_dict()

    def refund(
        self,
        order_id: typing.Optional[str] = None,
        session_id: typing.Optional[str] = None,
        amount: typing.Optional[str] = None,
        tracking_key: typing.Optional[str] = None,
    ) -> dict:
        headers = None
        if tracking_key:
            headers = {
                "Tracking-Key": tracking_key,
            }
        ottu_py_response = self.ops(
            operation="refund",
            order_id=order_id,
            session_id=session_id,
            amount=amount,
            headers=headers,
        )
        if ottu_py_response.success:
            self.refresh()
        return ottu_py_response.as_dict()

    def void(
        self,
        order_id: typing.Optional[str] = None,
        session_id: typing.Optional[str] = None,
        tracking_key: typing.Optional[str] = None,
    ) -> dict:
        headers = None
        if tracking_key:
            headers = {
                "Tracking-Key": tracking_key,
            }
        ottu_py_response = self.ops(
            operation="void",
            order_id=order_id,
            session_id=session_id,
            headers=headers,
        )
        if ottu_py_response.success:
            self.refresh()
        return ottu_py_response.as_dict()

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
            "type": "sandbox" if self.ottu.is_sandbox else "production",
        }
        payload = remove_empty_values(payload)
        return self.ottu.send_request(
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

    def get_pg_codes(self, plugin, currency, tokenizable=False) -> list:
        if self.payment_methods:
            return [pm.code for pm in self.payment_methods]

        response = self.get_payment_methods(
            plugin=plugin,
            currencies=[
                currency,
            ],
            tokenizable=tokenizable,
        )
        if not response["success"]:
            raise APIInterruptError(**response)
        return [pm["code"] for pm in response["response"]["payment_methods"]]

    def get_auto_debit_pg_codes(self, plugin, currency) -> list:
        # There is no way to identify the
        # cached payment method supports auto debit or not.
        # So, we are calling the API again.
        response = self.get_payment_methods(
            plugin=plugin,
            currencies=[
                currency,
            ],
            tokenizable=True,
        )
        if not response["success"]:
            raise APIInterruptError(**response)
        return [pm["code"] for pm in response["response"]["payment_methods"]]

    def get_token_from_db(self, agreement, customer_id) -> str:
        raise NotImplementedError("Please implement this method in your subclass")

    @interruption_handler
    def checkout_autoflow(
        self,
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
    ):
        pg_codes = self.get_pg_codes(plugin=txn_type, currency=currency_code)
        return self.create(
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

    @interruption_handler
    def auto_debit_autoflow(
        self,
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
        token: typing.Optional[str] = None,
    ):
        """
        Completes the auto debit flow by automatically
        identifying the "latest" payment method and the token.
        """
        if not token:
            token = self.get_token_from_db(agreement=agreement, customer_id=customer_id)
        if not pg_codes:
            pg_codes = self.get_auto_debit_pg_codes(
                plugin=txn_type,
                currency=currency_code,
            )
        checkout_response = self.create(
            txn_type=txn_type,
            amount=amount,
            currency_code=currency_code,
            pg_codes=pg_codes,
            payment_type="auto_debit",
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
        if not checkout_response["success"]:
            raise APIInterruptError(**checkout_response)
        session_id = checkout_response["response"]["session_id"]
        return self.auto_debit(token=token, session_id=session_id)
