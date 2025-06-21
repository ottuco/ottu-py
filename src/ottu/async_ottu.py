from functools import wraps

try:
    from asgiref.sync import sync_to_async
except ImportError:
    raise ImportError(
        "asgiref is required for async support. "
        "Install with: pip install 'ottu-py[django]' or pip install 'ottu-py[fastapi]'",
    )

from .ottu import Ottu


def async_method(func):
    """Decorator to convert sync methods to async using sync_to_async."""

    @wraps(func)
    async def wrapper(*args, **kwargs):
        return await sync_to_async(func)(*args, **kwargs)

    return wrapper


class OttuAsync:
    """Async wrapper for Ottu SDK using sync_to_async.

    This ensures 100% identical behavior between sync and async versions
    while providing proper async/await support.
    """

    def __init__(self, *args, **kwargs):
        """Initialize with same arguments as Ottu."""
        self._ottu = Ottu(*args, **kwargs)

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        # Close the underlying httpx client if it has an aclose method
        if hasattr(self._ottu.request_session, "aclose"):
            await self._ottu.request_session.aclose()
        elif hasattr(self._ottu.request_session, "close"):
            self._ottu.request_session.close()

    # Proxy properties to underlying Ottu instance
    @property
    def merchant_id(self):
        return self._ottu.merchant_id

    @property
    def customer_id(self):
        return self._ottu.customer_id

    @property
    def env_type(self):
        return self._ottu.env_type

    @property
    def session(self):
        """Return async-wrapped session."""
        return AsyncSessionWrapper(self._ottu.session)

    @property
    def cards(self):
        """Return async-wrapped cards."""
        return AsyncCardWrapper(self._ottu.cards)

    # Async-wrapped methods
    @async_method
    def send_request(self, *args, **kwargs):
        return self._ottu.send_request(*args, **kwargs)

    @async_method
    def checkout(self, *args, **kwargs):
        return self._ottu.checkout(*args, **kwargs)

    @async_method
    def auto_debit(self, *args, **kwargs):
        return self._ottu.auto_debit(*args, **kwargs)

    @async_method
    def checkout_autoflow(self, *args, **kwargs):
        return self._ottu.checkout_autoflow(*args, **kwargs)

    @async_method
    def auto_debit_autoflow(self, *args, **kwargs):
        return self._ottu.auto_debit_autoflow(*args, **kwargs)

    @async_method
    def get_payment_methods(self, *args, **kwargs):
        return self._ottu.get_payment_methods(*args, **kwargs)

    @async_method
    def raw(self, *args, **kwargs):
        return self._ottu.raw(*args, **kwargs)


class AsyncSessionWrapper:
    """Async wrapper for Session class."""

    def __init__(self, session):
        self._session = session

    # Proxy properties
    @property
    def session_id(self):
        return self._session.session_id

    @property
    def checkout_url(self):
        return self._session.checkout_url

    @property
    def payment_methods(self):
        return self._session.payment_methods

    # Async-wrapped methods
    @async_method
    def create(self, *args, **kwargs):
        return self._session.create(*args, **kwargs)

    @async_method
    def retrieve(self, *args, **kwargs):
        return self._session.retrieve(*args, **kwargs)

    @async_method
    def update(self, *args, **kwargs):
        return self._session.update(*args, **kwargs)

    @async_method
    def refresh(self, *args, **kwargs):
        return self._session.refresh(*args, **kwargs)

    @async_method
    def auto_debit(self, *args, **kwargs):
        return self._session.auto_debit(*args, **kwargs)

    @async_method
    def capture(self, *args, **kwargs):
        return self._session.capture(*args, **kwargs)

    @async_method
    def refund(self, *args, **kwargs):
        return self._session.refund(*args, **kwargs)

    @async_method
    def void(self, *args, **kwargs):
        return self._session.void(*args, **kwargs)

    @async_method
    def cancel(self, *args, **kwargs):
        return self._session.cancel(*args, **kwargs)

    @async_method
    def expire(self, *args, **kwargs):
        return self._session.expire(*args, **kwargs)

    @async_method
    def delete(self, *args, **kwargs):
        return self._session.delete(*args, **kwargs)


class AsyncCardWrapper:
    """Async wrapper for Card class."""

    def __init__(self, cards):
        self._cards = cards

    @property
    def customer_id(self):
        """Get customer ID from the underlying cards object."""
        return self._cards.ottu.customer_id

    def __repr__(self):
        return f"AsyncCard({self.customer_id})"

    # Async-wrapped methods
    @async_method
    def get_cards(self, *args, **kwargs):
        return self._cards.get_cards(*args, **kwargs)

    @async_method
    def list(self, *args, **kwargs):
        return self._cards.list(*args, **kwargs)

    @async_method
    def get(self, *args, **kwargs):
        return self._cards.get(*args, **kwargs)

    @async_method
    def delete(self, *args, **kwargs):
        return self._cards.delete(*args, **kwargs)
