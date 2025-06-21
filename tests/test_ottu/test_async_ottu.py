import pytest
from unittest.mock import AsyncMock, patch

from ottu import OttuAsync
from ottu.auth import APIKeyAuth
from ottu.enums import TxnType


@pytest.fixture
def ottu_async():
    return OttuAsync(
        merchant_id="merchant.id.ottu.dev",
        auth=APIKeyAuth("test-api-key"),
        is_sandbox=True,
    )


@pytest.mark.asyncio
async def test_ottu_async_init(ottu_async):
    """Test basic OttuAsync initialization."""
    assert ottu_async.merchant_id == "merchant.id.ottu.dev"
    assert ottu_async.host_url == "https://merchant.id.ottu.dev"
    assert ottu_async.is_sandbox is True
    assert ottu_async.env_type == "sandbox"
    assert ottu_async.timeout == 30
    

@pytest.mark.asyncio
async def test_ottu_async_context_manager(ottu_async):
    """Test OttuAsync can be used as an async context manager."""
    async with ottu_async as client:
        assert client.merchant_id == "merchant.id.ottu.dev"
    # Session should be closed after exiting context


@pytest.mark.asyncio
async def test_ottu_async_send_request():
    """Test async send_request method."""
    with patch('httpx.AsyncClient.request') as mock_request:
        # Mock response
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": True, "data": "test"}
        mock_request.return_value = mock_response
        
        ottu_async = OttuAsync(
            merchant_id="merchant.id.ottu.dev",
            auth=APIKeyAuth("test-api-key"),
            is_sandbox=True,
        )
        
        response = await ottu_async.send_request(
            path="/test",
            method="GET"
        )
        
        assert response.success is True
        assert response.status_code == 200
        
        await ottu_async.close()


@pytest.mark.asyncio
async def test_ottu_async_checkout():
    """Test async checkout method."""
    with patch('httpx.AsyncClient.request') as mock_request:
        # Mock response
        from unittest.mock import Mock
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "session_id": "test-session-123",
            "checkout_url": "https://checkout.url",
            "amount": "20.23",
            "currency_code": "KWD"
        }
        mock_request.return_value = mock_response
        
        ottu_async = OttuAsync(
            merchant_id="merchant.id.ottu.dev",
            auth=APIKeyAuth("test-api-key"),
            is_sandbox=True,
        )
        
        response = await ottu_async.checkout(
            txn_type=TxnType.PAYMENT_REQUEST,
            amount="20.23",
            currency_code="KWD",
            pg_codes=["mpgs", "ottu_pg"],
            customer_phone="+96550000000",
            order_no="1234567890",
        )
        
        assert response["success"] is True
        assert response["response"]["session_id"] == "test-session-123"
        
        await ottu_async.close()


@pytest.mark.asyncio
async def test_ottu_async_get_payment_methods():
    """Test async get_payment_methods method."""
    with patch('httpx.AsyncClient.request') as mock_request:
        # Mock response
        from unittest.mock import Mock
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "payment_methods": [
                {"code": "mpgs", "name": "Mastercard Payment Gateway Service"},
                {"code": "ottu_pg", "name": "Ottu Payment Gateway"}
            ]
        }
        mock_request.return_value = mock_response
        
        ottu_async = OttuAsync(
            merchant_id="merchant.id.ottu.dev",
            auth=APIKeyAuth("test-api-key"),
            is_sandbox=True,
        )
        
        response = await ottu_async.get_payment_methods(
            plugin="payment_request",
            currencies=["KWD"]
        )
        
        assert response["success"] is True
        assert len(response["response"]["payment_methods"]) == 2
        
        await ottu_async.close()


@pytest.mark.asyncio
async def test_ottu_async_cards():
    """Test async cards property and methods."""
    with patch('httpx.AsyncClient.request') as mock_request:
        # Mock response
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"token": "card-token-123", "last_four": "1234", "brand": "visa"}
        ]
        mock_request.return_value = mock_response
        
        ottu_async = OttuAsync(
            merchant_id="merchant.id.ottu.dev",
            auth=APIKeyAuth("test-api-key"),
            is_sandbox=True,
            customer_id="customer-123"
        )
        
        # Test cards property
        cards = ottu_async.cards
        assert cards is not None
        
        # Test async card methods
        response = await cards.list()
        assert response["success"] is True
        
        await ottu_async.close()


@pytest.mark.asyncio
async def test_ottu_async_session_operations():
    """Test async session operations."""
    with patch('httpx.AsyncClient.request') as mock_request:
        # Mock response for create
        from unittest.mock import Mock
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "session_id": "test-session-123",
            "amount": "20.23",
            "state": "created"
        }
        mock_request.return_value = mock_response
        
        ottu_async = OttuAsync(
            merchant_id="merchant.id.ottu.dev",
            auth=APIKeyAuth("test-api-key"),
            is_sandbox=True,
        )
        
        # Test session create
        response = await ottu_async.session.create(
            txn_type=TxnType.PAYMENT_REQUEST,
            amount="20.23",
            currency_code="KWD",
            pg_codes=["mpgs"]
        )
        
        assert response["success"] is True
        assert response["response"]["session_id"] == "test-session-123"
        
        # Test session retrieve
        mock_response.json.return_value = {
            "session_id": "test-session-123",
            "amount": "20.23",
            "state": "pending"
        }
        
        response = await ottu_async.session.retrieve("test-session-123")
        assert response["success"] is True
        
        await ottu_async.close()