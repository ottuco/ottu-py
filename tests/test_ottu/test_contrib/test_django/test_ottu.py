import pytest

from ottu.contrib.django.models import Checkout

pytestmark = pytest.mark.django_db


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
