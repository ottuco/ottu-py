from inspect import signature

import pytest

from ottu import Ottu
from ottu.errors import ValidationError
from ottu.session import Session

from .mixins import OttuAutoDebitMixin, OttuCheckoutMixin


class TestSessionCreate(OttuCheckoutMixin):
    def get_method_ref(self):
        return Session.create

    def get_method(self, instance: Ottu):
        return instance.session.create

    def test_checkout_with_dynamic_args(
        self,
        httpx_mock,
        auth_api_key,
        payload_minimal_checkout,
        response_checkout,
    ):
        """
        Test the `Ottu.checkout` method with dynamic parameters.
        """
        match_json = {
            "type": "payment_request",
            "currency_code": "KWD",
            "amount": "12.34",
            "pg_codes": [
                "KNET",
            ],
            "payment_type": "one_off",
            "customer_id": "test-customer-jpg",
            "extra_name": "John",
            "extra_age": 18,
        }
        httpx_mock.add_response(
            url="https://test.ottu.dev/b/checkout/v1/pymt-txn/",
            method="POST",
            status_code=200,
            match_json=match_json,
        )
        ottu = Ottu(merchant_id="test.ottu.dev", auth=auth_api_key)
        # Make the request
        ottu.checkout(extra_name="John", extra_age=18, **payload_minimal_checkout)


class TestSessionRetrieve:
    def test_retrieve_missing_session_id(
        self,
        auth_api_key,
    ):
        """
        The `session_id` must be available before calling the `retrieve(...)` method
        """
        # Initiate Ottu
        ottu = Ottu(merchant_id="test.ottu.dev", auth=auth_api_key)

        # Make sure the `ottu.session` is not set
        assert ottu.session.session_id is None

        # Call the `Ottu.session.retrieve()` method
        with pytest.raises(TypeError):
            # because missing `session_id` in the context
            ottu.session.retrieve()

    def test_retrieve(
        self,
        auth_api_key,
        httpx_mock,
        response_checkout,
    ):
        session_id = "10039bbdadb8ef80dd9e16e200c241b139684a8d"
        httpx_mock.add_response(
            url=f"https://test.ottu.dev/b/checkout/v1/pymt-txn/{session_id}",
            method="GET",
            status_code=200,
            json=response_checkout,
        )

        # Initiate Ottu
        ottu = Ottu(merchant_id="test.ottu.dev", auth=auth_api_key)

        # Make sure the `ottu.session` is not set
        assert ottu.session.session_id is None

        # Call the `Ottu.session.retrieve()` method
        response = ottu.session.retrieve(session_id=session_id)
        # Assert the responses
        expected_response = {
            "success": True,
            "status_code": 200,
            "endpoint": f"/b/checkout/v1/pymt-txn/{session_id}",
            "error": {},
            "response": response_checkout,
        }
        assert response == expected_response
        assert ottu.session.session_id == session_id

    def test_retrieve_error(
        self,
        auth_api_key,
        httpx_mock,
        response_checkout,
    ):
        session_id = "10039bbdadb8ef80dd9e16e200c241b139684a8d"
        httpx_mock.add_response(
            url=f"https://test.ottu.dev/b/checkout/v1/pymt-txn/{session_id}",
            method="GET",
            status_code=502,
            json={"detail": "Any error from upstream"},
        )

        # Initiate Ottu
        ottu = Ottu(merchant_id="test.ottu.dev", auth=auth_api_key)

        # Make sure the `ottu.session` is not set
        assert ottu.session.session_id is None

        # Call the `Ottu.session.retrieve()` method
        response = ottu.session.retrieve(session_id=session_id)
        # Assert the responses
        expected_response = {
            "success": False,
            "status_code": 502,
            "endpoint": f"/b/checkout/v1/pymt-txn/{session_id}",
            "error": {"detail": "Any error from upstream"},
            "response": {},
        }
        assert response == expected_response
        assert ottu.session.session_id is None


class TestSessionRefresh:
    def test_refresh(
        self,
        httpx_mock,
        auth_api_key,
        payload_minimal_checkout,
        response_checkout,
    ):
        session_id = "10039bbdadb8ef80dd9e16e200c241b139684a8d"
        httpx_mock.add_response(
            url="https://test.ottu.dev/b/checkout/v1/pymt-txn/",
            method="POST",
            status_code=200,
            json=response_checkout,
        )
        httpx_mock.add_response(
            url=f"https://test.ottu.dev/b/checkout/v1/pymt-txn/{session_id}",
            method="GET",
            status_code=200,
            json=response_checkout,
        )

        ottu = Ottu(merchant_id="test.ottu.dev", auth=auth_api_key)

        # Make sure the `ottu.session` is not set
        assert ottu.session.session_id is None

        # Make the request
        response = ottu.checkout(**payload_minimal_checkout)

        assert response["success"] is True
        assert ottu.session.session_id is not None

        # Call the `Ottu.session.retrieve()` method
        response = ottu.session.refresh()
        # Assert the responses
        expected_response = {
            "success": True,
            "status_code": 200,
            "endpoint": f"/b/checkout/v1/pymt-txn/{session_id}",
            "error": {},
            "response": response_checkout,
        }
        assert response == expected_response
        assert ottu.session.session_id == session_id

    def test_refresh_fail(
        self,
        httpx_mock,
        auth_api_key,
        payload_minimal_checkout,
        response_checkout,
    ):
        session_id = "10039bbdadb8ef80dd9e16e200c241b139684a8d"
        httpx_mock.add_response(
            url="https://test.ottu.dev/b/checkout/v1/pymt-txn/",
            method="POST",
            status_code=200,
            json=response_checkout,
        )
        httpx_mock.add_response(
            url=f"https://test.ottu.dev/b/checkout/v1/pymt-txn/{session_id}",
            method="GET",
            status_code=502,
            json={"detail": "Any error from upstream"},
        )

        ottu = Ottu(merchant_id="test.ottu.dev", auth=auth_api_key)

        # Make sure the `ottu.session` is not set
        assert ottu.session.session_id is None

        # Make the request
        response = ottu.checkout(**payload_minimal_checkout)

        assert response["success"] is True
        assert ottu.session.session_id is not None

        # Call the `Ottu.session.retrieve()` method
        response = ottu.session.refresh()
        assert response is None

    def test_refresh_without_session_id(
        self,
        httpx_mock,
        auth_api_key,
        payload_minimal_checkout,
        response_checkout,
    ):
        ottu = Ottu(merchant_id="test.ottu.dev", auth=auth_api_key)

        # Make sure the `ottu.session` is not set
        assert ottu.session.session_id is None

        # Make the request
        response = ottu.session.refresh()

        assert response is None


class TestSessionAutoDebit(OttuAutoDebitMixin):
    def get_method_ref(self):
        return Session.auto_debit

    def get_method(self, instance: Ottu):
        return instance.session.auto_debit


class TestSessionUpdate:
    def test_session_update_signature(
        self,
        signature_info_session_update,
    ):
        parameters = dict(signature(Session.update).parameters)
        parameters.pop("self")
        required_fields = {
            "currency_code",
            "amount",
            "txn_type",
            "agreement",
            "pg_codes",
        }
        optional_fields = set(parameters) - required_fields
        assert required_fields == signature_info_session_update["required_fields"]
        assert optional_fields == signature_info_session_update["optional_fields"]

    def test_session_update_fail(
        self,
        httpx_mock,
        response_checkout,
        auth_api_key,
        ottu_instance,
    ):
        session_id = "10039bbdadb8ef80dd9e16e200c241b139684a8d"
        httpx_mock.add_response(
            url=f"https://test.ottu.dev/b/checkout/v1/pymt-txn/{session_id}",
            method="PATCH",
            status_code=502,
            json={"detail": "Any error from upstream"},
        )

        ottu_instance.session.retrieve(session_id=session_id)
        response = ottu_instance.session.update(amount="1234.56")

        assert response["success"] is False
        assert ottu_instance.session.amount == "12.340"  # Not changed

    def test_session_update_minimal(
        self,
        httpx_mock,
        response_checkout,
        auth_api_key,
        ottu_instance,
    ):
        session_id = "10039bbdadb8ef80dd9e16e200c241b139684a8d"
        httpx_mock.add_response(
            url=f"https://test.ottu.dev/b/checkout/v1/pymt-txn/{session_id}",
            method="PATCH",
            status_code=200,
            json={**response_checkout, "amount": "1234.56"},
        )

        ottu_instance.session.retrieve(session_id=session_id)
        response = ottu_instance.session.update(amount="1234.56")

        assert response["success"] is True
        assert ottu_instance.session.amount == "1234.56"

    def test_session_update_with_attachment(
        self,
        httpx_mock,
        response_checkout,
        auth_api_key,
        ottu_instance,
    ):
        session_id = "10039bbdadb8ef80dd9e16e200c241b139684a8d"
        httpx_mock.add_response(
            url=f"https://test.ottu.dev/b/checkout/v1/pymt-txn/{session_id}",
            method="PATCH",
            status_code=200,
            json={
                **response_checkout,
                "amount": "1234.56",
                "attachment": "https://cdn.something.dev/tests/demo-file.txt",
            },
        )

        ottu_instance.session.retrieve(session_id=session_id)
        response = ottu_instance.session.update(
            amount="1234.56",
            attachment="tests/demo-file.txt",
        )

        assert response["success"] is True
        assert ottu_instance.session.amount == "1234.56"
        assert (
            ottu_instance.session.attachment
            == "https://cdn.something.dev/tests/demo-file.txt"
        )


class TestOps:
    @pytest.mark.parametrize(
        "op_name, extra_params",
        [
            ("cancel", []),
            ("expire", []),
            ("delete", []),
            ("capture", ["amount", "tracking_key"]),
            ("refund", ["amount", "tracking_key"]),
            ("void", ["tracking_key"]),
        ],
    )
    def test_signature(
        self,
        signature_ops,
        op_name,
        extra_params,
    ):
        parameters = dict(signature(getattr(Session, op_name)).parameters)
        parameters.pop("self")
        required_fields = {
            name for name, param in parameters.items() if param.default is param.empty
        }
        optional_fields = set(parameters) - required_fields
        assert required_fields == signature_ops["required_fields"]
        assert optional_fields == signature_ops["optional_fields"] | set(extra_params)

    @pytest.mark.parametrize(
        "op_name",
        ["capture", "refund", "void"],
    )
    def test_op_method_success_with_tracking_key(
        self,
        ottu_instance,
        httpx_mock,
        response_checkout,
        op_name,
    ):
        httpx_mock.add_response(
            url="https://test.ottu.dev/b/pbl/v2/operation/",
            method="POST",
            status_code=200,
            json={"detail": "Success"},
        )

        method = getattr(ottu_instance.session, op_name)
        response = method(
            order_id="test-order-id",
            session_id="test-session-id",
            tracking_key="test-tracking-key",
        )

        assert response["success"] is True

    @pytest.mark.parametrize(
        "session_id, order_id",
        [
            (None, None),
            ("10039bbdadb8ef80dd9e16e200c241b139684a8d", None),
            (None, "10039bbdadb8ef80dd9e16e200c241b139684a8d"),
        ],
    )
    @pytest.mark.parametrize(
        "op_name",
        ["cancel", "expire", "delete", "capture", "refund", "void"],
    )
    def test_op_method_success(
        self,
        ottu_instance,
        httpx_mock,
        response_checkout,
        session_id,
        order_id,
        op_name,
    ):
        httpx_mock.add_response(
            url="https://test.ottu.dev/b/pbl/v2/operation/",
            method="POST",
            status_code=200,
            json={"detail": "Success"},
        )

        method = getattr(ottu_instance.session, op_name)
        response = method(
            order_id=order_id,
            session_id=session_id,
        )

        assert response["success"] is True

    @pytest.mark.parametrize(
        "session_id, order_id",
        [
            (None, None),
            ("10039bbdadb8ef80dd9e16e200c241b139684a8d", None),
            (None, "10039bbdadb8ef80dd9e16e200c241b139684a8d"),
        ],
    )
    @pytest.mark.parametrize(
        "op_name",
        ["cancel", "expire", "delete", "capture", "refund", "void"],
    )
    @pytest.mark.parametrize(
        "success_status",
        [True, False],
    )
    def test_op_method_fail(
        self,
        ottu_instance,
        httpx_mock,
        response_checkout,
        session_id,
        order_id,
        op_name,
        success_status,
    ):
        httpx_mock.add_response(
            url="https://test.ottu.dev/b/pbl/v2/operation/",
            method="POST",
            status_code=200 if success_status else 500,
            json={"detail": "Success" if success_status else "Failed"},
        )

        method = getattr(ottu_instance.session, op_name)
        response = method(
            order_id=order_id,
            session_id=session_id,
        )

        assert response["success"] is success_status

    @pytest.mark.parametrize(
        "op_name",
        ["cancel", "expire", "delete", "capture", "refund", "void"],
    )
    def test_op_method_without_session_id(
        self,
        auth_api_key,
        op_name,
    ):
        ottu = Ottu(merchant_id="test.ottu.dev", auth=auth_api_key)
        method = getattr(ottu.session, op_name)
        with pytest.raises(ValidationError) as exc:
            method()
            assert exc.msg == "session_id or order_id is required"
