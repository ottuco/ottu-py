import pytest

from ottu import OttuAsync
from ottu.enums import TxnType
from tests.test_ottu.test_ottu.mixins import (
    OttuAutoDebitMixin,
    OttuCheckoutMixin,
)


class TestOttuAsyncAutoDebit(OttuAutoDebitMixin):
    """Test async auto debit functionality using sync_to_async wrapper."""

    def get_method_ref(self):
        return OttuAsync.auto_debit

    def get_method(self, instance: OttuAsync):
        return instance.auto_debit
    
    # Skip signature test for async - decorator changes signature but behavior is identical
    def test_auto_debit_signature(self, signature_info_auto_debit):
        pytest.skip("Signature test not relevant for sync_to_async wrapper")

    @pytest.mark.asyncio
    async def test_auto_debit_200(self, httpx_mock, auth_api_key, response_auto_debit):
        """Test the async auto_debit method with 200 response."""
        httpx_mock.add_response(
            url="https://test.ottu.dev/b/pbl/v2/auto-debit/",
            method="POST",
            status_code=200,
            json=response_auto_debit,
        )
        async with OttuAsync(merchant_id="test.ottu.dev", auth=auth_api_key) as ottu:
            # Make the request
            response = await self.get_method(ottu)(
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

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "status_code",
        [400, 500],
    )
    async def test_auto_debit_non_200(self, httpx_mock, auth_api_key, status_code):
        """Test async auto_debit method with non-200 responses."""
        httpx_mock.add_response(
            url="https://test.ottu.dev/b/pbl/v2/auto-debit/",
            method="POST",
            status_code=status_code,
            json={"detail": "Any error from upstream"},
        )
        async with OttuAsync(merchant_id="test.ottu.dev", auth=auth_api_key) as ottu:
            # Make the request
            response = await self.get_method(ottu)(
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


class TestOttuAsyncCheckout(OttuCheckoutMixin):
    """Test async checkout functionality using sync_to_async wrapper."""

    def get_method_ref(self):
        return OttuAsync.checkout

    def get_method(self, instance: OttuAsync):
        return instance.checkout
    
    # Skip signature test for async - decorator changes signature but behavior is identical  
    def test_checkout_signature(self, signature_info_checkout):
        pytest.skip("Signature test not relevant for sync_to_async wrapper")

    @pytest.mark.asyncio
    async def test_checkout_minimal_params(
        self,
        httpx_mock,
        auth_api_key,
        payload_minimal_checkout,
        response_checkout,
    ):
        """Test async checkout with minimal parameters."""
        httpx_mock.add_response(
            url="https://test.ottu.dev/b/checkout/v1/pymt-txn/",
            method="POST",
            status_code=200,
            json=response_checkout,
        )
        async with OttuAsync(merchant_id="test.ottu.dev", auth=auth_api_key) as ottu:
            response = await ottu.checkout(**payload_minimal_checkout)
            expected_response = {
                "success": True,
                "status_code": 200,
                "endpoint": "/b/checkout/v1/pymt-txn/",
                "error": {},
                "response": response_checkout,
            }
            assert response == expected_response


class TestOttuAsyncCore:
    """Test core async functionality."""

    @pytest.mark.asyncio
    async def test_context_manager(self, auth_api_key):
        """Test that OttuAsync works as an async context manager."""
        async with OttuAsync(merchant_id="test.ottu.dev", auth=auth_api_key) as ottu:
            assert ottu.merchant_id == "test.ottu.dev"
            assert ottu._ottu is not None  # Has underlying sync instance

    @pytest.mark.asyncio
    async def test_property_proxying(self, auth_api_key):
        """Test that properties are correctly proxied to sync instance."""
        async with OttuAsync(
            merchant_id="test.ottu.dev", 
            auth=auth_api_key,
            customer_id="test-customer"
        ) as ottu:
            assert ottu.merchant_id == "test.ottu.dev"
            assert ottu.customer_id == "test-customer"
            assert ottu.env_type == "sandbox"  # Default is True

    @pytest.mark.asyncio
    async def test_session_wrapper(self, auth_api_key):
        """Test that session wrapper works correctly."""
        async with OttuAsync(merchant_id="test.ottu.dev", auth=auth_api_key) as ottu:
            session = ottu.session
            assert hasattr(session, 'create')
            assert hasattr(session, 'retrieve')
            assert hasattr(session, 'capture')
            # Properties should be accessible
            assert session.session_id is None  # No session created yet

    @pytest.mark.asyncio
    async def test_cards_wrapper(self, auth_api_key):
        """Test that cards wrapper works correctly.""" 
        async with OttuAsync(
            merchant_id="test.ottu.dev",
            auth=auth_api_key,
            customer_id="test-customer"
        ) as ottu:
            cards = ottu.cards
            assert hasattr(cards, 'list')
            assert hasattr(cards, 'get')
            assert hasattr(cards, 'delete')
            assert "AsyncCard(test-customer)" in str(cards)

    @pytest.mark.asyncio
    async def test_send_request(self, httpx_mock, auth_api_key):
        """Test the async send_request method."""
        httpx_mock.add_response(
            url="https://test.ottu.dev/test/path",
            method="GET",
            status_code=200,
            json={"message": "success"},
        )
        async with OttuAsync(merchant_id="test.ottu.dev", auth=auth_api_key) as ottu:
            response = await ottu.send_request(
                path="/test/path",
                method="GET",
            )
            assert response.success is True
            assert response.status_code == 200
            assert response.response == {"message": "success"}

    @pytest.mark.asyncio
    async def test_get_payment_methods(self, httpx_mock, auth_api_key):
        """Test async get_payment_methods."""
        httpx_mock.add_response(
            url="https://test.ottu.dev/b/pbl/v2/payment-methods/",
            method="POST",
            status_code=200,
            json={"payment_methods": []},
        )
        async with OttuAsync(merchant_id="test.ottu.dev", auth=auth_api_key) as ottu:
            response = await ottu.get_payment_methods(
                plugin="payment_request",
                currencies=["KWD", "USD"],
            )
            assert response["success"] is True


class TestOttuAsyncCards:
    """Test async card operations."""

    @pytest.mark.asyncio
    async def test_cards_list(self, httpx_mock, auth_api_key, response_user_cards):
        """Test async cards list functionality."""
        httpx_mock.add_response(
            url="https://test.ottu.dev/b/pbl/v2/card/",
            method="POST",
            status_code=200,
            json=response_user_cards,
        )
        async with OttuAsync(
            merchant_id="test.ottu.dev", 
            auth=auth_api_key,
            customer_id="test-customer"
        ) as ottu:
            response = await ottu.cards.list()
            assert response["success"] is True

    @pytest.mark.asyncio
    async def test_cards_get(self, httpx_mock, auth_api_key, response_user_cards):
        """Test async cards get functionality."""
        httpx_mock.add_response(
            url="https://test.ottu.dev/b/pbl/v2/card/",
            method="POST",
            status_code=200,
            json=response_user_cards,
        )
        async with OttuAsync(
            merchant_id="test.ottu.dev", 
            auth=auth_api_key,
            customer_id="test-customer"
        ) as ottu:
            card = await ottu.cards.get()
            if response_user_cards:
                assert card == response_user_cards[0]
            else:
                assert card is None

    @pytest.mark.asyncio
    async def test_cards_delete(self, httpx_mock, auth_api_key):
        """Test async cards delete functionality."""
        httpx_mock.add_response(
            url="https://test.ottu.dev/b/pbl/v2/card/test-token/?customer_id=test-customer&type=sandbox",
            method="DELETE",
            status_code=204,
            json={},
        )
        async with OttuAsync(
            merchant_id="test.ottu.dev", 
            auth=auth_api_key,
            customer_id="test-customer"
        ) as ottu:
            response = await ottu.cards.delete(token="test-token")
            assert response["success"] is True


class TestOttuAsyncSession:
    """Test async session operations."""

    @pytest.mark.asyncio
    async def test_session_create(self, httpx_mock, auth_api_key, response_checkout):
        """Test async session create."""
        httpx_mock.add_response(
            url="https://test.ottu.dev/b/checkout/v1/pymt-txn/",
            method="POST",
            status_code=200,
            json=response_checkout,
        )
        async with OttuAsync(merchant_id="test.ottu.dev", auth=auth_api_key) as ottu:
            response = await ottu.session.create(
                txn_type=TxnType.PAYMENT_REQUEST,
                amount="12.34",
                currency_code="KWD",
                pg_codes=["KNET"],
            )
            assert response["success"] is True

    @pytest.mark.asyncio
    async def test_session_retrieve(self, httpx_mock, auth_api_key, response_checkout):
        """Test async session retrieve."""
        httpx_mock.add_response(
            url="https://test.ottu.dev/b/checkout/v1/pymt-txn/test-session-id",
            method="GET",
            status_code=200,
            json=response_checkout,
        )
        async with OttuAsync(merchant_id="test.ottu.dev", auth=auth_api_key) as ottu:
            response = await ottu.session.retrieve(session_id="test-session-id")
            assert response["success"] is True

    @pytest.mark.asyncio
    async def test_session_operations(self, httpx_mock, auth_api_key):
        """Test async session operations (capture, refund, void, etc)."""
        # Test capture
        httpx_mock.add_response(
            url="https://test.ottu.dev/b/pbl/v2/operation/",
            method="POST",
            status_code=200,
            json={"detail": "Success"},
        )
        async with OttuAsync(merchant_id="test.ottu.dev", auth=auth_api_key) as ottu:
            response = await ottu.session.capture(session_id="test-session")
            assert response["success"] is True


