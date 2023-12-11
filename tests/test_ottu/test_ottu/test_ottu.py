from inspect import signature

from ottu.ottu import Ottu
from tests.test_ottu.test_ottu.mixins import (
    MethodRefMixin,
    OttuAutoDebitMixin,
    OttuCheckoutMixin,
)


class TestOttuAutoDebit(OttuAutoDebitMixin):
    def get_method_ref(self):
        return Ottu.auto_debit

    def get_method(self, instance: Ottu):
        return instance.auto_debit


class TestOttuCheckout(OttuCheckoutMixin):
    def get_method_ref(self):
        return Ottu.checkout

    def get_method(self, instance: Ottu):
        return instance.checkout


class TestOttuMisc:
    def test_card_cache(self, auth_api_key):
        ottu = Ottu(merchant_id="test.ottu.dev", auth=auth_api_key)
        cards_1 = ottu.cards
        assert cards_1
        cards_2 = ottu.cards
        assert cards_1 is cards_2


class TestOttuCheckoutAutoFlow(MethodRefMixin):
    def get_method_ref(self):
        return Ottu.checkout_autoflow

    def get_method(self, instance: Ottu):
        return instance.checkout_autoflow

    def test_signature(self, signature_info_checkout_auto_flow):
        """
        Test supported parameters for the `Ottu.checkout_autoflow(...)` method.
        """
        parameters = dict(signature(self.get_method_ref()).parameters)
        parameters.pop("self")
        required_fields = {
            name for name, param in parameters.items() if param.default is param.empty
        }
        optional_fields = set(parameters) - required_fields
        assert required_fields == signature_info_checkout_auto_flow["required_fields"]
        assert optional_fields == signature_info_checkout_auto_flow["optional_fields"]

    def test_checkout_autoflow_success(
        self,
        httpx_mock,
        response_checkout,
        response_payment_methods,
        auth_api_key,
        payload_checkout_autoflow,
    ):
        httpx_mock.add_response(
            url="https://test.ottu.dev/b/checkout/v1/pymt-txn/",
            method="POST",
            status_code=200,
            json=response_checkout,
        )
        httpx_mock.add_response(
            url="https://test.ottu.dev/b/pbl/v2/payment-methods/",
            method="POST",
            status_code=200,
            json=response_payment_methods,
        )

        ottu = Ottu(merchant_id="test.ottu.dev", auth=auth_api_key)

        # Make sure the `ottu.session` is not set
        assert ottu.session.session_id is None

        # Make the request
        response = self.get_method(ottu)(**payload_checkout_autoflow)

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

    def test_checkout_autoflow_from_cache(
        self,
        httpx_mock,
        response_checkout,
        auth_api_key,
        payload_checkout_autoflow,
        payload_minimal_checkout,
    ):
        httpx_mock.add_response(
            url="https://test.ottu.dev/b/checkout/v1/pymt-txn/",
            method="POST",
            status_code=200,
            json=response_checkout,
        )
        httpx_mock.add_response(
            url="https://test.ottu.dev/b/checkout/v1/pymt-txn/",
            method="POST",
            status_code=200,
            json=response_checkout,
        )
        ottu = Ottu(merchant_id="test.ottu.dev", auth=auth_api_key)

        # Make sure the `ottu.session` is not set
        assert ottu.session.session_id is None

        ottu.checkout(**payload_minimal_checkout)

        # Make the request
        response = self.get_method(ottu)(**payload_checkout_autoflow)

        expected_response = {
            "success": True,
            "status_code": 200,
            "endpoint": "/b/checkout/v1/pymt-txn/",
            "error": {},
            "response": response_checkout,
        }
        assert response == expected_response

        # Check whether the `ottu.session` updated or not by new response
        assert ottu.session.pg_codes == ["ottu_pg_kwd_tkn"]

    def test_checkout_autoflow_pg_code_fetch_error(
        self,
        httpx_mock,
        auth_api_key,
        payload_checkout_autoflow,
    ):
        httpx_mock.add_response(
            url="https://test.ottu.dev/b/pbl/v2/payment-methods/",
            method="POST",
            status_code=500,
            json={"detail": "Internal Server Error"},
        )

        ottu = Ottu(merchant_id="test.ottu.dev", auth=auth_api_key)

        # Make sure the `ottu.session` is not set
        assert ottu.session.session_id is None

        # Make the request
        response = self.get_method(ottu)(**payload_checkout_autoflow)

        expected_response = {
            "success": False,
            "status_code": 500,
            "endpoint": "/b/pbl/v2/payment-methods/",
            "error": {"detail": "Internal Server Error"},
            "response": {},
        }
        assert response == expected_response


class TestCheckoutAutoDebitAutoFlow:
    def test_signature(self, signature_info_auto_debit_autoflow):
        """
        Test supported parameters for the `Ottu.checkout_autoflow(...)` method.
        """
        parameters = dict(signature(Ottu.auto_debit_autoflow).parameters)
        parameters.pop("self")
        required_fields = {
            name for name, param in parameters.items() if param.default is param.empty
        }
        optional_fields = set(parameters) - required_fields
        assert required_fields == signature_info_auto_debit_autoflow["required_fields"]
        assert optional_fields == signature_info_auto_debit_autoflow["optional_fields"]

    def test_auto_debit_autoflow_with_token(
        self,
        httpx_mock,
        response_payment_methods,
        auth_api_key,
        payload_auto_debit_autoflow,
        response_checkout,
        response_auto_debit,
    ):
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

        ottu = Ottu(merchant_id="test.ottu.dev", auth=auth_api_key)

        response = ottu.auto_debit_autoflow(
            token="test-token",
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

    def test_auto_debit_autoflow_with_pg_codes(
        self,
        httpx_mock,
        response_payment_methods,
        auth_api_key,
        payload_auto_debit_autoflow,
        response_checkout,
        response_auto_debit,
    ):
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

        ottu = Ottu(merchant_id="test.ottu.dev", auth=auth_api_key)

        response = ottu.auto_debit_autoflow(
            token="test-token",
            pg_codes=["ottu_pg_kwd_tkn"],
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

    def test_auto_debit_autoflow_pymt_mthd_error(
        self,
        httpx_mock,
        response_payment_methods,
        auth_api_key,
        payload_auto_debit_autoflow,
        response_checkout,
        response_auto_debit,
    ):
        """
        Error while trying to get the Auto-Debit payment methods.
        """
        httpx_mock.add_response(
            url="https://test.ottu.dev/b/pbl/v2/payment-methods/",
            method="POST",
            status_code=500,
            json={"detail": "Internal Server Error"},
        )

        ottu = Ottu(merchant_id="test.ottu.dev", auth=auth_api_key)

        response = ottu.auto_debit_autoflow(
            token="test-token",
            **payload_auto_debit_autoflow,
        )

        expected_response = {
            "success": False,
            "status_code": 500,
            "endpoint": "/b/pbl/v2/payment-methods/",
            "error": {"detail": "Internal Server Error"},
            "response": {},
        }
        assert response == expected_response

    def test_auto_debit_autoflow_checkout_error(
        self,
        httpx_mock,
        response_payment_methods,
        auth_api_key,
        payload_auto_debit_autoflow,
        response_checkout,
        response_auto_debit,
    ):
        httpx_mock.add_response(
            url="https://test.ottu.dev/b/pbl/v2/payment-methods/",
            method="POST",
            status_code=200,
            json=response_payment_methods,
        )
        httpx_mock.add_response(
            url="https://test.ottu.dev/b/checkout/v1/pymt-txn/",
            method="POST",
            status_code=500,
            json={"detail": "Internal Server Error"},
        )

        ottu = Ottu(merchant_id="test.ottu.dev", auth=auth_api_key)

        response = ottu.auto_debit_autoflow(
            token="test-token",
            **payload_auto_debit_autoflow,
        )

        expected_response = {
            "success": False,
            "status_code": 500,
            "endpoint": "/b/checkout/v1/pymt-txn/",
            "error": {"detail": "Internal Server Error"},
            "response": {},
        }
        assert response == expected_response

    def test_auto_debit_autoflow_auto_debit_error(
        self,
        httpx_mock,
        response_payment_methods,
        auth_api_key,
        payload_auto_debit_autoflow,
        response_checkout,
        response_auto_debit,
    ):
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
            status_code=500,
            json={"detail": "Internal Server Error"},
        )

        ottu = Ottu(merchant_id="test.ottu.dev", auth=auth_api_key)

        response = ottu.auto_debit_autoflow(
            token="test-token",
            **payload_auto_debit_autoflow,
        )

        expected_response = {
            "success": False,
            "status_code": 500,
            "endpoint": "/b/pbl/v2/auto-debit/",
            "error": {"detail": "Internal Server Error"},
            "response": {},
        }
        assert response == expected_response
