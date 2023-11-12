from django.conf import settings

MERCHANT_ID = getattr(settings, "DJ_OTTU_MERCHANT_ID")

# Authentication
# `BasicAuth`
AUTH_USERNAME = getattr(settings, "DJ_OTTU_AUTH_USERNAME", "")
AUTH_PASSWORD = getattr(settings, "DJ_OTTU_AUTH_PASSWORD", "")

# `APIKeyAuth`
AUTH_API_KEY = getattr(settings, "DJ_OTTU_AUTH_API_KEY", "")


ABSTRACT_CHECKOUT_MODEL = getattr(settings, "DJ_OTTU_ABSTRACT_CHECKOUT_MODEL", False)
ABSTRACT_WEBHOOK_MODEL = getattr(settings, "DJ_OTTU_ABSTRACT_WEBHOOK_MODEL", False)
WEBHOOK_KEY = getattr(settings, "DJ_OTTU_WEBHOOK_KEY", "")
WEBHOOK_URL = getattr(settings, "DJ_OTTU_WEBHOOK_URL", "")
