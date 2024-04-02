import pytest

from ottu.auth import APIKeyAuth, BasicAuth
from ottu.enums import TxnType

from . import fake_data


# Auth
@pytest.fixture
def auth_basic():
    return BasicAuth(username="username", password="password")


@pytest.fixture
def auth_api_key():
    return APIKeyAuth(api_key="U6cGFzc3dvcmQ")


# Payloads


@pytest.fixture
def payload_minimal_checkout():
    """
    This payload is used to test the
    `Ottu.checkout(...)` method with
    minimal parameters.
    """
    return {
        "txn_type": TxnType.PAYMENT_REQUEST,
        "amount": "12.34",
        "currency_code": "KWD",
        "pg_codes": ["KNET"],
        "customer_id": "test-customer-jpg",
    }


@pytest.fixture
def payload_auto_debit_autoflow():
    return {
        "txn_type": TxnType.PAYMENT_REQUEST,
        "amount": "12.34",
        "currency_code": "KWD",
        "customer_id": "test-customer-jpg",
        "agreement": {
            "id": "test-agreement-id",
            "amount_variability": "fixed",
            "cycle_interval_days": 30,
            "expiry_date": "2023-11-07",
            "frequency": "monthly",
            "total_cycles": 12,
        },
    }


@pytest.fixture
def payload_checkout_autoflow():
    return {
        "txn_type": TxnType.PAYMENT_REQUEST,
        "amount": "12.34",
        "currency_code": "KWD",
        "customer_id": "test-customer-jpg",
    }


@pytest.fixture
def payload_minimal_auto_flow():
    return {
        "txn_type": TxnType.PAYMENT_REQUEST,
        "amount": "12.34",
        "currency_code": "KWD",
        "customer_id": "test-customer-jpg",
        "agreement": {
            "id": "test-agreement-id",
            "amount_variability": "fixed",
            "cycle_interval_days": 30,
            "expiry_date": "2023-11-07",
            "frequency": "monthly",
            "total_cycles": 12,
        },
    }


@pytest.fixture
def payload_minimal_auto_debit_checkout(payload_minimal_auto_flow):
    """
    This payload is used to test the
    `Ottu.auto_debit_checkout(...)` method
    with minimal parameters.
    """
    return {
        "pg_codes": ["KNET"],
        **payload_minimal_auto_flow,
    }


# Signature Info


@pytest.fixture
def signature_info_auto_debit_autoflow():
    required_fields = {
        "amount",
        "customer_id",
        "agreement",
        "txn_type",
        "currency_code",
    }
    optional_fields = {
        "pg_codes",
        "attachment",
        "billing_address",
        "card_acceptance_criteria",
        "customer_email",
        "customer_first_name",
        "customer_last_name",
        "customer_phone",
        "due_datetime",
        "email_recipients",
        "expiration_time",
        "extra",
        "generate_qr_code",
        "language",
        "mode",
        "notifications",
        "order_no",
        "product_type",
        "redirect_url",
        "shopping_address",
        "shortify_attachment_url",
        "shortify_checkout_url",
        "token",
        "vendor_name",
        "webhook_url",
        "include_sdk_setup_preload",
        "checkout_extra_args",
    }
    return {
        "required_fields": required_fields,
        "optional_fields": optional_fields,
    }


@pytest.fixture
def signature_info_checkout_auto_flow():
    required_fields = {"currency_code", "txn_type", "amount"}
    optional_fields = {
        "expiration_time",
        "email_recipients",
        "due_datetime",
        "vendor_name",
        "attachment",
        "product_type",
        "webhook_url",
        "order_no",
        "agreement",
        "mode",
        "card_acceptance_criteria",
        "extra",
        "customer_email",
        "notifications",
        "shortify_attachment_url",
        "shortify_checkout_url",
        "shopping_address",
        "customer_first_name",
        "payment_type",
        "redirect_url",
        "language",
        "customer_phone",
        "generate_qr_code",
        "customer_id",
        "billing_address",
        "customer_last_name",
        "checkout_extra_args",
        "include_sdk_setup_preload",
    }
    return {
        "required_fields": required_fields,
        "optional_fields": optional_fields,
    }


@pytest.fixture
def signature_info_auto_debit():
    required_fields = {"token", "session_id"}
    optional_fields = set()
    return {
        "required_fields": required_fields,
        "optional_fields": optional_fields,
    }


@pytest.fixture
def signature_info_auto_debit_checkout():
    required_fields = {"currency_code", "amount", "pg_codes", "txn_type", "agreement"}
    optional_fields = {
        "attachment",
        "billing_address",
        "card_acceptance_criteria",
        "customer_email",
        "customer_first_name",
        "customer_id",
        "customer_last_name",
        "customer_phone",
        "due_datetime",
        "email_recipients",
        "expiration_time",
        "extra",
        "generate_qr_code",
        "language",
        "mode",
        "notifications",
        "order_no",
        "product_type",
        "redirect_url",
        "shopping_address",
        "shortify_attachment_url",
        "shortify_checkout_url",
        "vendor_name",
        "webhook_url",
    }
    return {
        "required_fields": required_fields,
        "optional_fields": optional_fields,
    }


@pytest.fixture
def signature_info_checkout():
    required_fields = {
        "txn_type",
        "amount",
        "currency_code",
        "pg_codes",
        "kwargs",
    }
    optional_fields = {
        "payment_type",
        "customer_id",
        "customer_email",
        "customer_phone",
        "customer_first_name",
        "customer_last_name",
        "agreement",
        "card_acceptance_criteria",
        "attachment",
        "billing_address",
        "due_datetime",
        "email_recipients",
        "expiration_time",
        "extra",
        "generate_qr_code",
        "language",
        "mode",
        "notifications",
        "order_no",
        "product_type",
        "redirect_url",
        "shopping_address",
        "shortify_attachment_url",
        "shortify_checkout_url",
        "vendor_name",
        "webhook_url",
        "include_sdk_setup_preload",
    }
    return {
        "required_fields": required_fields,
        "optional_fields": optional_fields,
    }


@pytest.fixture
def signature_info_session_update():
    required_fields = {
        "currency_code",
        "txn_type",
        "agreement",
        "amount",
        "pg_codes",
    }
    optional_fields = {
        "attachment",
        "billing_address",
        "customer_email",
        "customer_first_name",
        "customer_id",
        "customer_last_name",
        "customer_phone",
        "due_datetime",
        "email_recipients",
        "expiration_time",
        "extra",
        "generate_qr_code",
        "language",
        "mode",
        "notifications",
        "order_no",
        "product_type",
        "redirect_url",
        "shopping_address",
        "shortify_attachment_url",
        "shortify_checkout_url",
        "vendor_name",
        "webhook_url",
    }
    return {
        "required_fields": required_fields,
        "optional_fields": optional_fields,
    }


@pytest.fixture
def signature_ops():
    required_fields = set()
    optional_fields = {"order_id", "session_id"}
    return {
        "required_fields": required_fields,
        "optional_fields": optional_fields,
    }


# Responses


@pytest.fixture
def response_checkout():
    return fake_data.response_checkout


@pytest.fixture
def response_auto_debit():
    return fake_data.response_auto_debit


@pytest.fixture
def response_payment_methods():
    return fake_data.response_payment_methods


@pytest.fixture
def response_user_cards():
    return fake_data.response_user_cards


# Ottu instances


@pytest.fixture
def ottu_instance(auth_api_key, httpx_mock, response_checkout):
    session_id = "10039bbdadb8ef80dd9e16e200c241b139684a8d"
    httpx_mock.add_response(
        url=f"https://test.ottu.dev/b/checkout/v1/pymt-txn/{session_id}",
        method="GET",
        status_code=200,
        json=response_checkout,
    )
    from ottu import Ottu

    ottu = Ottu(merchant_id="test.ottu.dev", auth=auth_api_key)
    ottu.session.retrieve(session_id=session_id)
    return ottu
