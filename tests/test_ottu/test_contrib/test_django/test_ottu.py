import pytest
from django.core.exceptions import ImproperlyConfigured

from ottu.auth import BasicAuth
from ottu.contrib.django.core.ottu import _generate_instance
from ottu.contrib.django.models import Checkout

pytestmark = pytest.mark.django_db


class TestDefaultOttuInit:
    mock_path = "ottu.contrib.django.core.ottu.conf.AUTH"

    def test_invalid_cls_path(self, mocker):
        mock_auth = mocker.patch(self.mock_path)
        mock_auth.copy.return_value = {"class": "path.to.invalid.AuthClass"}
        with pytest.raises(ImproperlyConfigured) as exc_info:
            _generate_instance()
        assert "The 'class' key is not a valid import path" == str(exc_info.value)

    def test_without_cls_field(self, mocker):
        mock_auth = mocker.patch(self.mock_path)
        mock_auth.copy.return_value = {}
        with pytest.raises(ImproperlyConfigured) as exc_info:
            _generate_instance()
        assert "The 'class' key is required in the 'AUTH' dictionary" == str(
            exc_info.value,
        )

    def test_without_auth_settings(self, mocker):
        mock_auth = mocker.patch(self.mock_path)
        mock_auth.copy.side_effect = AttributeError

        with pytest.raises(ImproperlyConfigured) as exc_info:
            _generate_instance()
        assert "Must set `OTTU_AUTH` in the settings file" == str(exc_info.value)

    def test_generate_instance(self):
        ottu = _generate_instance()
        assert isinstance(ottu.auth, BasicAuth)


class TestOttuAuth:
    def test_init_basic_auth(self, httpx_mock, ottu):
        httpx_mock.add_response(
            url="https://test.ottu.dev/any/path",
            method="GET",
            status_code=200,
            json={"message": "success"},
        )

        ottu.send_request(path="/any/path", method="GET")
        request = httpx_mock.get_request()
        auth_header = request.headers.get("Authorization")
        assert auth_header == "Basic ZGpfdXNlcm5hbWU6ZGpfcGFzc3dvcmQ="

    def test_init_api_key_auth(self):
        # TODO: Need a way to test any dynamic auth by mocking the settings
        ...


class TestOttuCheckoutModel:
    def test_create_checkout_instance(
        self,
        httpx_mock,
        response_checkout,
        payload_minimal_checkout,
        ottu,
    ):
        httpx_mock.add_response(
            url="https://test.ottu.dev/b/checkout/v1/pymt-txn/",
            method="POST",
            status_code=200,
            json=response_checkout,
        )

        # Make sure the `ottu.session` is not set
        assert ottu.session.session_id is None

        # Make the request
        response = ottu.checkout(**payload_minimal_checkout)

        # Assert the responses
        expected_response = {
            "success": True,
            "status_code": 200,
            "endpoint": "/b/checkout/v1/pymt-txn/",
            "error": {},
            "response": response_checkout,
        }
        assert response == expected_response

        # Check whether the `ottu.session` updated or not by new response
        assert ottu.session.session_id == response_checkout["session_id"]

        # Try to pull Django DB instance from DB
        checkout_obj = Checkout.objects.get(session_id=response_checkout["session_id"])
        assert checkout_obj.session_id == response_checkout["session_id"]

    def test_auto_debit_autoflow_token_not_found(
        self,
        response_payment_methods,
        auth_api_key,
        payload_auto_debit_autoflow,
        response_checkout,
        response_auto_debit,
        ottu,
    ):
        response = ottu.auto_debit_autoflow(
            **payload_auto_debit_autoflow,
        )

        expected_response = {
            "success": False,
            "status_code": 400,
            "endpoint": "",
            "error": {"detail": "Token not found in the database"},
            "response": {},
        }
        assert response == expected_response

    def test_auto_debit_autoflow(
        self,
        httpx_mock,
        response_payment_methods,
        auth_api_key,
        payload_auto_debit_autoflow,
        response_checkout,
        response_auto_debit,
        ottu,
    ):
        Checkout.objects.create(
            session_id=response_checkout["session_id"],
            token="test-token",
            agreement={
                "id": "test-agreement-id",
                # other details
            },
            customer_id=response_checkout["customer_id"],
        )
        httpx_mock.add_response(
            url="https://test.ottu.dev/b/pbl/v2/payment-methods/",
            method="POST",
            status_code=200,
            json=response_payment_methods,
        )
        httpx_mock.add_response(
            url="https://test.ottu.dev/b/checkout/v1/pymt-txn/",
            method="POST",
            status_code=200,
            json=response_checkout,
        )
        httpx_mock.add_response(
            url="https://test.ottu.dev/b/pbl/v2/auto-debit/",
            method="POST",
            status_code=200,
            json=response_auto_debit,
        )

        response = ottu.auto_debit_autoflow(
            **payload_auto_debit_autoflow,
        )

        expected_response = {
            "success": True,
            "status_code": 200,
            "endpoint": "/b/pbl/v2/auto-debit/",
            "error": {},
            "response": response_auto_debit,
        }
        assert response == expected_response
