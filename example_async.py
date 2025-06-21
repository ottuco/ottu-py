#!/usr/bin/env python3
"""
Example demonstrating async usage of the Ottu SDK.
"""
import asyncio

from ottu import OttuAsync
from ottu.auth import APIKeyAuth
from ottu.enums import TxnType


async def main():
    """Demo async functionality."""
    print("🚀 Starting Ottu Async SDK Demo...")

    # Initialize async client
    async with OttuAsync(
        merchant_id="merchant.example.ottu.dev",
        auth=APIKeyAuth("demo-api-key"),
        is_sandbox=True,
        timeout=30,
    ) as ottu:
        print(f"✅ Connected to {ottu.merchant_id} ({ottu.env_type})")

        # Note: These will return error responses with real API calls since we're using demo credentials
        # But they demonstrate the async API structure and response format

        # Example 1: Create checkout session
        print("\n📦 Creating checkout session...")
        response = await ottu.checkout(
            txn_type=TxnType.PAYMENT_REQUEST,
            amount="25.50",
            currency_code="USD",
            pg_codes=["stripe", "paypal"],
            customer_email="demo@example.com",
            customer_phone="+1234567890",
            order_no="ORDER-12345",
        )
        print(f"   Success: {response.get('success', False)}")
        if not response.get('success'):
            error_detail = response.get('error', {}).get('detail', 'Unknown error')
            print(f"   Error (expected with demo credentials): {error_detail}")

        # Example 2: Get payment methods
        print("\n💳 Getting payment methods...")
        payment_methods = await ottu.get_payment_methods(
            plugin="payment_request",
            currencies=["USD", "EUR"],
        )
        print(f"   Success: {payment_methods.get('success', False)}")
        if not payment_methods.get('success'):
            error_detail = payment_methods.get('error', {}).get('detail', 'Unknown error')
            print(f"   Error (expected with demo credentials): {error_detail}")

        # Example 3: Card operations
        print("\n🎫 Accessing card operations...")
        cards = ottu.cards
        print(f"   Cards instance: {cards}")

        # List cards - will return error response with demo credentials
        card_response = await cards.list()
        print(f"   Cards list success: {card_response.get('success', False)}")

        # Example 4: Session operations
        print("\n🔄 Accessing session operations...")
        session = ottu.session
        print(f"   Session instance: {session}")

        # Session operations - will return error response with demo credentials
        if response.get('response', {}).get('session_id'):
            session_data = await session.retrieve(session_id=response['response']['session_id'])
            print(f"   Session retrieve success: {session_data.get('success', False)}")
        else:
            print("   No session ID available from checkout response")

        print("\n🎉 Demo completed successfully!")
        print(f"   Client type: {type(ottu).__name__}")
        print("   Supports async context manager: ✅")
        print("   All methods are async: ✅")


if __name__ == "__main__":
    asyncio.run(main())

