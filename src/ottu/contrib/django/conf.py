from django.conf import settings

# Merchant Related
MERCHANT_ID: str = getattr(settings, "OTTU_MERCHANT_ID")

# Authentication
AUTH: dict = getattr(settings, "OTTU_AUTH")

# Abstract models
ABSTRACT_CHECKOUT_MODEL: bool = getattr(settings, "OTTU_ABSTRACT_CHECKOUT_MODEL", False)
ABSTRACT_WEBHOOK_MODEL: bool = getattr(settings, "OTTU_ABSTRACT_WEBHOOK_MODEL", False)

# Webhook
WEBHOOK_KEY: str = getattr(settings, "OTTU_WEBHOOK_KEY", "")
WEBHOOK_URL: str = getattr(settings, "OTTU_WEBHOOK_URL", "")

# Misc
IS_SANDBOX: bool = getattr(settings, "OTTU_IS_SANDBOX", False)
