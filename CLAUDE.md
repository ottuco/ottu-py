# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is the official Python SDK for the Ottu Checkout API. It provides a clean interface for payment processing, session management, and card operations with optional Django integration. The SDK supports both synchronous and asynchronous operations.

## Development Commands

### Setup
```bash
# Install for development with all dependencies
pip install -e .[dev]

# Install with Django support
pip install -e .[django,dev]
```

### Testing
```bash
# Run all tests
python -m pytest

# Run tests with coverage (must maintain 80% minimum)
python -m pytest --cov=src --cov-fail-under=80

# Run a specific test file
python -m pytest tests/test_specific.py

# Run tests with verbose output
python -m pytest -v
```

### Code Quality
```bash
# Run all pre-commit checks (black, isort, flake8, mypy)
bash pre-commit.sh

# Individual tools
black src tests
isort src tests
flake8 src tests
mypy src
```

### Version Management
```bash
# Version bump (updates version in all relevant files)
bump2version patch  # 1.0.0 → 1.0.1
bump2version minor  # 1.0.1 → 1.1.0
bump2version major  # 1.1.0 → 2.0.0
```

## Architecture

### Core Components

1. **Ottu Classes**: Main SDK entry points that orchestrate all operations
   - **Ottu** (`src/ottu/ottu.py`): Synchronous client
   - **OttuAsync** (`src/ottu/async_ottu.py`): Asynchronous client
   - Both handle authentication setup and manage HTTP client configuration
   - Provide access to Session and Card operations

2. **Session Management**: Handles payment checkout sessions
   - **Session** (`src/ottu/session.py`): Synchronous session operations
   - **AsyncSession** (`src/ottu/async_session.py`): Asynchronous session operations
   - Create, retrieve, and update sessions
   - Execute operations: capture, refund, void, cancel, expire
   - Auto-flow feature for automatic payment gateway selection

3. **Card Management**: Manages customer payment cards
   - **Card** (`src/ottu/cards.py`): Synchronous card operations
   - **AsyncCard** (`src/ottu/async_cards.py`): Asynchronous card operations
   - List, get, and delete stored cards

4. **Request Handling** (`src/ottu/request.py`): HTTP request processing
   - **BaseRequestResponseHandler**: Shared logic for request/response handling
   - **RequestResponseHandler**: Synchronous HTTP requests using httpx.Client
   - **AsyncRequestResponseHandler**: Asynchronous HTTP requests using httpx.AsyncClient

5. **Authentication** (`src/ottu/auth.py`): Multiple authentication strategies
   - APIKeyAuth: Simple API key authentication
   - BasicAuth: Username/password authentication
   - KeycloakPasswordAuth: OAuth2 password flow with Keycloak
   - KeycloakServiceAccountAuth: OAuth2 client credentials flow

6. **Django Integration** (`src/ottu/contrib/django/`): Optional Django app
   - Models: PaymentSession, PaymentSessionItem, PaymentSessionOperations
   - Views: Webhook handling with signature verification
   - Admin: Django admin interface for payment management
   - Settings: OTTU_* configuration in Django settings

### Request Flow

1. Client initializes Ottu with auth method and merchant ID
2. Operations go through request handler with auth headers
3. Responses are parsed into dataclasses for type safety
4. Errors raise specific exceptions (OttuHTTPException)

### Testing Approach

- Unit tests mock HTTP calls (never external services)
- Database operations use real database entries (SQLite for tests)
- Django tests use a test Django application setup
- Fixtures and fake data in `tests/conftest.py` and `tests/fake_data.py`

## Key Implementation Notes

1. **Error Handling**: All API errors raise `OttuHTTPException` with detailed error info
2. **Type Safety**: Uses dataclasses extensively for request/response objects
3. **Django Models**: Store payment data locally, sync with Ottu API
4. **Webhook Verification**: Always verify webhook signatures using `utils.validate_webhook_signature`
5. **Auto-flow**: When `pg_codes='auto'`, SDK selects payment gateway based on currency

## Django-Specific Notes

When working with Django integration:
1. Add `'ottu_py.contrib.django'` to INSTALLED_APPS
2. Configure OTTU_* settings in settings.py
3. Run migrations to create payment tables
4. Use provided views for webhook handling
5. Access admin interface for payment management

## Async Support

The SDK provides full async support with `OttuAsync` class:

```python
# Async usage
from ottu import OttuAsync
from ottu.auth import APIKeyAuth

async def main():
    async with OttuAsync(
        merchant_id="merchant.id.ottu.dev",
        auth=APIKeyAuth("your-secret-api-key"),
        is_sandbox=True
    ) as ottu:
        # Create checkout session
        response = await ottu.checkout(
            txn_type=TxnType.PAYMENT_REQUEST,
            amount="20.23",
            currency_code="KWD",
            pg_codes=["mpgs", "ottu_pg"],
            customer_phone="+96550000000",
            order_no="1234567890",
        )

        # Use cards
        cards = await ottu.cards.list()

        # Session operations
        await ottu.session.capture(session_id="session-123")
```

### Key Async Design Principles:
- **Minimal Code Duplication**: Async classes inherit from base classes where possible
- **Consistent API**: Async methods have the same signatures as sync methods
- **Context Manager Support**: `OttuAsync` supports `async with` for automatic cleanup
- **Shared Logic**: Request handling, response parsing, and business logic are shared

## Common Patterns

- Use real database entries for tests, mock only HTTP calls
- Follow existing code style (black, isort formatting)
- Add type hints to all new code
- Maintain 80% test coverage minimum
- Update CHANGELOG.md for user-facing changes
- For async code: always use `async with` for client lifecycle management
- When testing async code: use `pytest.mark.asyncio` and `unittest.mock.Mock` (not `AsyncMock` for httpx responses)
