# flake8: noqa

response_checkout = {
    "amount": "12.340",
    "checkout_url": "https://beta.ottu.net/b/checkout/redirect/start/?session_id=10039bbdadb8ef80dd9e16e200c241b139684a8d",
    "currency_code": "KWD",
    "customer_id": "test-customer-jpg",
    "due_datetime": "07/11/2023 09:40:38",
    "expiration_time": "1 00:00:00",
    "language": "en",
    "operation": "purchase",
    "payment_methods": [
        {
            "code": "ottu_pg_kwd_tkn",
            "name": "ottu_pg_kwd_tkn",
            "pg": "Ottu PG",
            "type": "sandbox",
            "amount": "12.340",
            "currency_code": "KWD",
            "fee": "0.000",
            "fee_description": "",
            "icon": "https://beta.ottu.net/media/gateway/settings/logos/Visa-MasterCard002_WIcgTQz.png",
            "flow": "redirect",
            "redirect_url": "https://pg.ottu.dev/checkout/YmV0YS5vdHR1Lm5ldA==/Z0FBQUFBQmxTZ1lXd3NXOXhDS1VpcURTR180ZENzMEhSN0xwNkVMTUJhQlJOWUl2cXdUUjlTVUN6NndmZDJncUFFZGFBRmlDQkRWaGZiWXYwaVlQUFFDWXc1NW8zX3pCX0tfaXBvOG5SaEl1NUs3eG9UZHJIQk1xZURvbkQzN1JhQXpKN2Jmeko4c1UwZjBLTy1XaG9mMy1HRGtKRU9DekNDZ0RjcDhORXNDYVJQRHVZS0V4VjBPVGVfYVlxd2lqNWI2T3BKT0g5NHZIVHFUQmJmT0MyaXNVV1FDQWpsQTBqV2dWZEo1bnlENU5ES2ZVeXJTdGJsTGlHQWhUdC1ZcXVMMFJmSHhtZi1qemlPQ2xpVjkzYW5YN3hwcV9iZ29LXzdyMkVsaWwzcDhRMjBhR0dJU0tQVEEtOGcxMUY3cElYSXE0a3NjZ2tTc00xSHlXYnUyQVpRQldVWmNLZ3RhS2JDZ1BvVUtUNWd5bjhpTUJMMTJEVEI2dDRFMDJTNkF3RFFaZTFTRkE3LUVvMm9qYU5IajRJVzBmdXlQTE1YU0NTek8yd1owOHNvY1BfbHZCMzVhRExIc0xrZHQxWW9GRVZqRzZPV2QxVHFqQnh5TUpBeHJQYU1fRjN1N3VkcEg0RHB3MWpIR1p5blp0Zlg5UzVQem15UXJmcU5IMlFhaVF2Z3JuZGxILXVETVpEckF5ZmZGbFRHZHlra0FfNGgtTnZUUlFxc0E0Z3VmVk5GQ3dabmdvbkgwbVNGY0lqMVVVVlI0UFlrTk5xV2hKaFZ0SXFmMTdyWFlQZnhCWEN5UjhKb1ZhMnItREpneHVfcC1TUmJ6RHZlY0xVZk9vUGZCczQzczgtMzhJQktpckx5MnVyTlk2Qmp5QlR4Z0tLd25tLTlQNTJNT1JrTjdwNndKWjBPbTk2ckFKQTJOU3NZeHU4bElnNG1BUFJaVlM=",
        },
    ],
    "payment_type": "one_off",
    "pg_codes": [
        "ottu_pg_kwd_tkn",
    ],
    "session_id": "10039bbdadb8ef80dd9e16e200c241b139684a8d",
    "state": "created",
    "type": "payment_request",
}
response_auto_debit = {
    "agreement": {
        "id": "test-auto-flow-id-123",
        "amount_variability": "variable",
        "expiry_date": "2023-11-07",
        "cycle_interval_days": 30,
        "total_cycles": 12,
        "frequency": "other",
        "type": "recurring",
    },
    "amount": "4.650",
    "amount_details": {
        "currency_code": "KWD",
        "amount": "4.650",
        "total": "4.650",
        "fee": "0.000",
    },
    "card_acceptance_criteria": {
        "min_expiry_time": 30,
    },
    "currency_code": "KWD",
    "customer_id": "test-customer-jpg",
    "gateway_account": "ottu_pg_kwd_tkn",
    "gateway_name": "mpgs",
    "gateway_response": {},
    "initiator": {},
    "message": "Unknown Error",
    "payment_type": "auto_debit",
    "reference_number": "BETTTaA8G8XE",
    "remaining_amount": "4.650",
    "result": "error",
    "session_id": "c0b425064e112735130914cb76eff8ce14ca8393",
    "signature": "63cfe04f3e20b337156cd33ca27f4c573ad743f7f96d8df9b61c202cb8c7fb93",
    "state": "paid",
}
response_payment_methods = {
    "customer_payment_methods": [
        "auto-debit",
        "ottu_pg_kwd_tkn",
    ],
    "payment_methods": [
        {
            "code": "ottu_pg_kwd_tkn",
            "name": "ottu_pg_kwd_tkn",
            "pg": "Ottu PG",
            "is_sandbox": True,
            "logo": "https://beta.ottu.net/media/gateway/settings/logos/Visa-MasterCard002_WIcgTQz.png",
            "wallets": [],
            "default_currency": "KWD",
            "accepted_currencies": [
                "KWD",
                "SAR",
                "BHD",
            ],
            "operation": "purchase",
            "operations": [
                "refund",
            ],
        },
    ],
}
response_user_cards = [
    {
        "customer_id": "test-customer-jpg",
        "brand": "VISA",
        "name_on_card": "ASDFFFF",
        "number": "**** 0026",
        "expiry_month": "01",
        "expiry_year": "39",
        "token": "9918766711067353",
        "pg_code": "ottu_pg_kwd_tkn",
        "is_preferred": True,
        "is_expired": False,
        "will_expire_soon": False,
        "cvv_required": True,
        "agreements": [
            "test-auto-flow-id",
            "test-auto-flow-id-1233332",
            "test-auto-flow-id-123",
        ],
    },
]
webhook_payload = {
    "amount": "86.000",
    "currency_code": "KWD",
    "customer_first_name": "example-customer",
    "signature": "6143b8ad4bd283540721ab000f6de746e722231aaaa90bc38f639081d3ff9f67",
}
