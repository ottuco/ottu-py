from inspect import signature

import pytest

from ottu import Ottu


class MethodRefMixin:
    def get_method_ref(self):
        raise NotImplementedError

    def get_method(self, instance: Ottu):
        raise NotImplementedError


class OttuAutoDebitMixin(MethodRefMixin):
    def test_auto_debit_signature(self, signature_info_auto_debit):
        """
        Test supported parameters for the `Ottu.auto_debit(...)` method.
        """
        parameters = dict(signature(self.get_method_ref()).parameters)
        parameters.pop("self")
        required_fields = {
            name for name, param in parameters.items() if param.default is param.empty
        }
        optional_fields = set(parameters) - required_fields
        assert required_fields == signature_info_auto_debit["required_fields"]
        assert optional_fields == signature_info_auto_debit["optional_fields"]

    def test_auto_debit_200(self, httpx_mock, auth_api_key, response_auto_debit):
        """
        Test the `Ottu.auto_debit(...)` method
        """
        httpx_mock.add_response(
            url="https://test.ottu.dev/b/pbl/v2/auto-debit/",
            method="POST",
            status_code=200,
            json=response_auto_debit,
        )
        ottu = Ottu(merchant_id="test.ottu.dev", auth=auth_api_key)

        # Make the request
        response = self.get_method(ottu)(
            token="test-token",
            session_id="test-session-id",
        )

        # Assert the responses
        expected_response = {
            "success": True,
            "status_code": 200,
            "endpoint": "/b/pbl/v2/auto-debit/",
            "error": {},
            "response": response_auto_debit,
        }
        assert response == expected_response

    @pytest.mark.parametrize(
        "status_code",
        [400, 500],
    )
    def test_auto_debit_non_200(self, httpx_mock, auth_api_key, status_code):
        httpx_mock.add_response(
            url="https://test.ottu.dev/b/pbl/v2/auto-debit/",
            method="POST",
            status_code=status_code,
            json={"detail": "Any error from upstream"},
        )
        ottu = Ottu(merchant_id="test.ottu.dev", auth=auth_api_key)

        # Make the request
        response = self.get_method(ottu)(
            token="test-token",
            session_id="test-session-id",
        )
        expected_response = {
            "success": False,
            "status_code": status_code,
            "endpoint": "/b/pbl/v2/auto-debit/",
            "response": {},
            "error": {"detail": "Any error from upstream"},
        }
        assert response == expected_response


class OttuCheckoutMixin(MethodRefMixin):
    """
    A few methods of `Ottu` class is a wrapper for the methods in `Session` class.
    Both methods should be identical in terms of functionality, and arguments.
    """

    def test_checkout_signature(self, signature_info_checkout):
        """
        Test supported parameters for the `Ottu.checkout` method.
        """
        parameters = dict(signature(self.get_method_ref()).parameters)
        parameters.pop("self")  # remove obvious `self` parameter
        required_fields = {
            name for name, param in parameters.items() if param.default is param.empty
        }
        optional_fields = set(parameters) - required_fields
        assert required_fields == signature_info_checkout["required_fields"]
        assert optional_fields == signature_info_checkout["optional_fields"]

    def test_checkout_minimal_params(
        self,
        httpx_mock,
        auth_api_key,
        payload_minimal_checkout,
        response_checkout,
    ):
        """
        Test the `Ottu.checkout` method with minimal parameters.
        """
        httpx_mock.add_response(
            url="https://test.ottu.dev/b/checkout/v1/pymt-txn/",
            method="POST",
            status_code=200,
            json=response_checkout,
        )
        ottu = Ottu(merchant_id="test.ottu.dev", auth=auth_api_key)

        # Make sure the `ottu.session` is not set
        assert ottu.session.session_id is None

        # Make the request
        response = self.get_method(ottu)(**payload_minimal_checkout)

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

    def test_checkout_with_attachment(
        self,
        httpx_mock,
        auth_api_key,
        payload_minimal_checkout,
        response_checkout,
    ):
        httpx_mock.add_response(
            url="https://test.ottu.dev/b/checkout/v1/pymt-txn/",
            method="POST",
            status_code=200,
            json=response_checkout,
        )
        ottu = Ottu(merchant_id="test.ottu.dev", auth=auth_api_key)

        # Make sure the `ottu.session` is not set
        assert ottu.session.session_id is None

        # Make the request
        response = self.get_method(ottu)(
            **{**payload_minimal_checkout, "attachment": "tests/demo-file.txt"},
        )

        request = httpx_mock.get_request()

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

        # Check the content type of the request
        assert "multipart/form-data" in request.headers["content-type"]
