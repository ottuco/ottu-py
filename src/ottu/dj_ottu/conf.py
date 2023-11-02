from django.conf import settings

from ..errors import ConfigurationError

MERCHANT_ID = getattr(settings, "DJ_OTTU_MERCHANT_ID")
AUTH_USERNAME = getattr(settings, "DJ_OTTU_AUTH_USERNAME", "")
AUTH_PASSWORD = getattr(settings, "DJ_OTTU_AUTH_PASSWORD", "")
AUTH_API_KEY = getattr(settings, "DJ_OTTU_AUTH_API_KEY", "")
ABSTRACT_CHECKOUT_MODEL = getattr(settings, "DJ_OTTU_ABSTRACT_CHECKOUT_MODEL", False)
ABSTRACT_WEBHOOK_MODEL = getattr(settings, "DJ_OTTU_ABSTRACT_WEBHOOK_MODEL", False)
WEBHOOK_KEY = getattr(settings, "DJ_OTTU_WEBHOOK_KEY", "")
WEBHOOK_URL = getattr(settings, "DJ_OTTU_WEBHOOK_URL", "")

# Validation
username_and_pass = AUTH_USERNAME and AUTH_PASSWORD
if not username_and_pass and not AUTH_API_KEY:
    raise ConfigurationError(
        "You must provide either `DJ_OTTU_AUTH_USERNAME` and "
        "`DJ_OTTU_AUTH_PASSWORD` or `DJ_OTTU_AUTH_API_KEY``",
    )
