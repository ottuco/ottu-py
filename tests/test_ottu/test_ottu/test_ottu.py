from inspect import signature

import pytest

from ottu.ottu import Ottu
from tests.test_ottu.test_ottu.mixins import OttuAutoDebitMixin, OttuCheckoutMixin


class TestOttuAutoDebit(OttuAutoDebitMixin):
    def get_method_ref(self):
        return Ottu.auto_debit

    def get_method(self, instance: Ottu):
        return instance.auto_debit


class TestOttuAutoDebitCheckout:
    def test_auto_debit_checkout_signature(self, signature_info_auto_debit_checkout):
        """
        Test supported parameters for the `Ottu.auto_debit_checkout(...)` method.
        """
        parameters = dict(signature(Ottu.auto_debit_checkout).parameters)
        parameters.pop("self")  # remove obvious `self` parameter
        required_fields = {
            name for name, param in parameters.items() if param.default is param.empty
        }
        optional_fields = set(parameters) - required_fields
        assert required_fields == signature_info_auto_debit_checkout["required_fields"]
        assert optional_fields == signature_info_auto_debit_checkout["optional_fields"]

    def test_auto_debit_checkout_minimal_params(
        self,
        httpx_mock,
        auth_api_key,
        payload_minimal_auto_debit_checkout,
        response_checkout,
    ):
        """
        Test the `Ottu.auto_debit_checkout(...)` method with minimal parameters.
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
        response = ottu.auto_debit_checkout(**payload_minimal_auto_debit_checkout)

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

    @pytest.mark.parametrize(
        "status_code",
        [400, 500],
    )
    def test_test_auto_debit_checkout_minimal_params_non_200(
        self,
        httpx_mock,
        auth_api_key,
        payload_minimal_auto_debit_checkout,
        status_code,
    ):
        httpx_mock.add_response(
            url="https://test.ottu.dev/b/checkout/v1/pymt-txn/",
            method="POST",
            status_code=status_code,
            json={"detail": "Any error from upstream"},
        )
        ottu = Ottu(merchant_id="test.ottu.dev", auth=auth_api_key)

        # Make the request
        response = ottu.auto_debit_checkout(**payload_minimal_auto_debit_checkout)
        expected_response = {
            "success": False,
            "status_code": status_code,
            "endpoint": "/b/checkout/v1/pymt-txn/",
            "response": {},
            "error": {"detail": "Any error from upstream"},
        }
        assert response == expected_response


class TestOttuAutoFlow:
    def test_auto_flow_signature(self, signature_info_auto_debit_checkout):
        """
        Test supported parameters for the `Ottu.auto_flow(...)` method.
        """
        parameters = dict(signature(Ottu.auto_flow).parameters)
        parameters.pop("self")
        required_fields = {
            "currency_code",
            "amount",
            "txn_type",
            "agreement",
            "pg_codes",
        }
        optional_fields = set(parameters) - required_fields
        expected_optional_fields = {
            "is_sandbox",
            *signature_info_auto_debit_checkout["optional_fields"],
        }
        assert required_fields == signature_info_auto_debit_checkout["required_fields"]
        assert optional_fields == expected_optional_fields

    def test_auto_flow(
        self,
        httpx_mock,
        auth_api_key,
        payload_minimal_auto_flow,
        response_checkout,
        response_payment_methods,
        response_user_cards,
        response_auto_debit,
    ):
        # Process:
        # 1. Mock call to get auto-debit PG info
        # 2. Mock call to get saved card token
        # 3. Mock call to auto-debit checkout
        # 4. Mock call to auto-debit using session ID (from 3rd step)

        # Mock Responses
        httpx_mock.add_response(
            url="https://test.ottu.dev/b/pbl/v2/payment-methods/",
            method="POST",
            status_code=200,
            json=response_payment_methods,
        )
        httpx_mock.add_response(
            url="https://test.ottu.dev/b/pbl/v2/card/",
            method="POST",
            status_code=200,
            json=response_user_cards,
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

        # Initiate Ottu
        ottu = Ottu(merchant_id="test.ottu.dev", auth=auth_api_key)

        # Make sure the `ottu.session` is not set
        assert ottu.session.session_id is None

        # Make the request
        response = ottu.auto_flow(**payload_minimal_auto_flow, is_sandbox=True)

        # Assert the responses
        expected_response = {
            "success": True,
            "status_code": 200,
            "endpoint": "/b/pbl/v2/auto-debit/",
            "error": {},
            "response": response_auto_debit,
        }
        assert response == expected_response
        assert ottu.session.session_id

    def test_auto_flow_payment_method_api_error(
        self,
        httpx_mock,
        auth_api_key,
        payload_minimal_auto_flow,
    ):
        httpx_mock.add_response(
            url="https://test.ottu.dev/b/pbl/v2/payment-methods/",
            method="POST",
            status_code=400,
            json={"detail": "Any error from upstream"},
        )

        # Initiate Ottu
        ottu = Ottu(merchant_id="test.ottu.dev", auth=auth_api_key)

        # Make sure the `ottu.session` is not set
        assert ottu.session.session_id is None

        # Make the request
        response = ottu.auto_flow(**payload_minimal_auto_flow, is_sandbox=True)

        # Assert the responses
        expected_response = {
            "endpoint": "/b/pbl/v2/payment-methods/",
            "error": {"detail": "No payment gateways found for auto debit"},
            "response": {},
            "status_code": 400,
            "success": False,
        }
        assert response == expected_response
        assert ottu.session.session_id is None

    def test_auto_flow_no_auto_debit_payment_method(
        self,
        httpx_mock,
        auth_api_key,
        payload_minimal_auto_flow,
    ):
        httpx_mock.add_response(
            url="https://test.ottu.dev/b/pbl/v2/payment-methods/",
            method="POST",
            status_code=200,
            json={
                "customer_payment_methods": [],
                "payment_methods": [],
            },
        )

        # Initiate Ottu
        ottu = Ottu(merchant_id="test.ottu.dev", auth=auth_api_key)

        # Make sure the `ottu.session` is not set
        assert ottu.session.session_id is None

        # Make the request
        response = ottu.auto_flow(**payload_minimal_auto_flow, is_sandbox=True)

        # Assert the responses
        expected_response = {
            "endpoint": "/b/pbl/v2/payment-methods/",
            "error": {"detail": "No payment gateways found for auto debit"},
            "response": {},
            "status_code": 400,
            "success": False,
        }
        assert response == expected_response
        assert ottu.session.session_id is None

    def test_auto_flow_more_than_1_auto_debit_payment_method(
        self,
        httpx_mock,
        auth_api_key,
        payload_minimal_auto_flow,
        response_payment_methods,
    ):
        httpx_mock.add_response(
            url="https://test.ottu.dev/b/pbl/v2/payment-methods/",
            method="POST",
            status_code=200,
            json={
                "customer_payment_methods": [],
                "payment_methods": response_payment_methods["payment_methods"] * 2,
            },
        )

        # Initiate Ottu
        ottu = Ottu(merchant_id="test.ottu.dev", auth=auth_api_key)

        # Make sure the `ottu.session` is not set
        assert ottu.session.session_id is None

        # Make the request
        response = ottu.auto_flow(**payload_minimal_auto_flow, is_sandbox=True)

        # Assert the responses
        expected_response = {
            "endpoint": "/b/pbl/v2/payment-methods/",
            "error": {"detail": "More than one payment gateway found for auto debit"},
            "response": {},
            "status_code": 400,
            "success": False,
        }
        assert response == expected_response
        assert ottu.session.session_id is None

    def test_auto_flow_user_card_fetch_error(
        self,
        httpx_mock,
        auth_api_key,
        payload_minimal_auto_flow,
        response_payment_methods,
    ):
        httpx_mock.add_response(
            url="https://test.ottu.dev/b/pbl/v2/payment-methods/",
            method="POST",
            status_code=200,
            json=response_payment_methods,
        )
        httpx_mock.add_response(
            url="https://test.ottu.dev/b/pbl/v2/card/",
            method="POST",
            status_code=400,
            json={"detail": "Any error from upstream"},
        )

        # Initiate Ottu
        ottu = Ottu(merchant_id="test.ottu.dev", auth=auth_api_key)

        # Make sure the `ottu.session` is not set
        assert ottu.session.session_id is None

        # Make the request
        response = ottu.auto_flow(**payload_minimal_auto_flow, is_sandbox=True)

        # Assert the responses
        expected_response = {
            "endpoint": "/b/pbl/v2/card/",
            "error": {"detail": "No cards found for auto debit"},
            "response": {},
            "status_code": 400,
            "success": False,
        }
        assert response == expected_response
        assert ottu.session.session_id is None

    def test_auto_flow_no_user_cards(
        self,
        httpx_mock,
        auth_api_key,
        payload_minimal_auto_flow,
        response_payment_methods,
    ):
        httpx_mock.add_response(
            url="https://test.ottu.dev/b/pbl/v2/payment-methods/",
            method="POST",
            status_code=200,
            json=response_payment_methods,
        )
        httpx_mock.add_response(
            url="https://test.ottu.dev/b/pbl/v2/card/",
            method="POST",
            status_code=200,
            json=[],
        )

        # Initiate Ottu
        ottu = Ottu(merchant_id="test.ottu.dev", auth=auth_api_key)

        # Make sure the `ottu.session` is not set
        assert ottu.session.session_id is None

        # Make the request
        response = ottu.auto_flow(**payload_minimal_auto_flow, is_sandbox=True)

        # Assert the responses
        expected_response = {
            "endpoint": "/b/pbl/v2/card/",
            "error": {"detail": "No cards found for auto debit"},
            "response": {},
            "status_code": 400,
            "success": False,
        }
        assert response == expected_response
        assert ottu.session.session_id is None

    def test_auto_flow_more_than_1_user_cards(
        self,
        httpx_mock,
        auth_api_key,
        payload_minimal_auto_flow,
        response_payment_methods,
        response_user_cards,
    ):
        httpx_mock.add_response(
            url="https://test.ottu.dev/b/pbl/v2/payment-methods/",
            method="POST",
            status_code=200,
            json=response_payment_methods,
        )
        httpx_mock.add_response(
            url="https://test.ottu.dev/b/pbl/v2/card/",
            method="POST",
            status_code=200,
            json=response_user_cards * 2,
        )

        # Initiate Ottu
        ottu = Ottu(merchant_id="test.ottu.dev", auth=auth_api_key)

        # Make sure the `ottu.session` is not set
        assert ottu.session.session_id is None

        # Make the request
        response = ottu.auto_flow(**payload_minimal_auto_flow, is_sandbox=True)

        # Assert the responses
        expected_response = {
            "endpoint": "/b/pbl/v2/card/",
            "error": {"detail": "More than one card found for auto debit"},
            "response": {},
            "status_code": 400,
            "success": False,
        }
        assert response == expected_response
        assert ottu.session.session_id is None

    def test_auto_flow_session_create_error(
        self,
        httpx_mock,
        auth_api_key,
        payload_minimal_auto_flow,
        response_payment_methods,
        response_user_cards,
    ):
        httpx_mock.add_response(
            url="https://test.ottu.dev/b/pbl/v2/payment-methods/",
            method="POST",
            status_code=200,
            json=response_payment_methods,
        )
        httpx_mock.add_response(
            url="https://test.ottu.dev/b/pbl/v2/card/",
            method="POST",
            status_code=200,
            json=response_user_cards,
        )
        httpx_mock.add_response(
            url="https://test.ottu.dev/b/checkout/v1/pymt-txn/",
            method="POST",
            status_code=400,
            json={"detail": "Any error from upstream"},
        )

        # Initiate Ottu
        ottu = Ottu(merchant_id="test.ottu.dev", auth=auth_api_key)

        # Make sure the `ottu.session` is not set
        assert ottu.session.session_id is None

        # Make the request
        response = ottu.auto_flow(**payload_minimal_auto_flow, is_sandbox=True)

        # Assert the responses
        expected_response = {
            "endpoint": "/b/checkout/v1/pymt-txn/",
            "error": {"detail": "Any error from upstream"},
            "response": {},
            "status_code": 400,
            "success": False,
        }
        assert response == expected_response
        assert ottu.session.session_id is None

    def test_auto_flow_auto_debit_error(
        self,
        httpx_mock,
        auth_api_key,
        payload_minimal_auto_flow,
        response_payment_methods,
        response_user_cards,
        response_checkout,
    ):
        httpx_mock.add_response(
            url="https://test.ottu.dev/b/pbl/v2/payment-methods/",
            method="POST",
            status_code=200,
            json=response_payment_methods,
        )
        httpx_mock.add_response(
            url="https://test.ottu.dev/b/pbl/v2/card/",
            method="POST",
            status_code=200,
            json=response_user_cards,
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
            status_code=400,
            json={"detail": "Any error from upstream"},
        )

        # Initiate Ottu
        ottu = Ottu(merchant_id="test.ottu.dev", auth=auth_api_key)

        # Make sure the `ottu.session` is not set
        assert ottu.session.session_id is None

        # Make the request
        response = ottu.auto_flow(**payload_minimal_auto_flow, is_sandbox=True)

        # Assert the responses
        expected_response = {
            "endpoint": "/b/pbl/v2/auto-debit/",
            "error": {"detail": "Any error from upstream"},
            "response": {},
            "status_code": 400,
            "success": False,
        }
        assert response == expected_response
        assert ottu.session.session_id


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
