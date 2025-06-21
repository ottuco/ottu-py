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
        timeout=30
    ) as ottu:
        print(f"✅ Connected to {ottu.merchant_id} ({ottu.env_type})")

        # Note: These will fail with real API calls since we're using demo credentials
        # But they demonstrate the async API structure

        try:
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
            print(f"   Response: {response.get('success', 'Error')}")
            
        except Exception as e:
            print(f"   Expected error (demo credentials): {type(e).__name__}")
        
        try:
            # Example 2: Get payment methods
            print("\n💳 Getting payment methods...")
            payment_methods = await ottu.get_payment_methods(
                plugin="payment_request",
                currencies=["USD", "EUR"]
            )
            print(f"   Response: {payment_methods.get('success', 'Error')}")
            
        except Exception as e:
            print(f"   Expected error (demo credentials): {type(e).__name__}")
        
        try:
            # Example 3: Card operations
            print("\n🎫 Accessing card operations...")
            cards = ottu.cards
            print(f"   Cards instance: {cards}")
            
            # List cards (would work with real credentials)
            # card_list = await cards.list()
            
        except Exception as e:
            print(f"   Expected error (demo credentials): {type(e).__name__}")
        
        try:
            # Example 4: Session operations
            print("\n🔄 Accessing session operations...")
            session = ottu.session
            print(f"   Session instance: {session}")
            
            # Session operations (would work with real credentials)
            # session_data = await session.retrieve("session-123")
            
        except Exception as e:
            print(f"   Expected error (demo credentials): {type(e).__name__}")
        
        print("\n🎉 Demo completed successfully!")
        print(f"   Client type: {type(ottu).__name__}")
        print("   Supports async context manager: ✅")
        print("   All methods are async: ✅")


if __name__ == "__main__":
    asyncio.run(main())