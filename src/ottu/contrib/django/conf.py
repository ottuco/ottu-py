from django.conf import settings

from ...errors import ConfigurationError

MERCHANT_ID = getattr(settings, "DJ_OTTU_MERCHANT_ID")

# Authentication
# `BasicAuth`
AUTH_USERNAME = getattr(settings, "DJ_OTTU_AUTH_USERNAME", "")
AUTH_PASSWORD = getattr(settings, "DJ_OTTU_AUTH_PASSWORD", "")

# `APIKeyAuth`
AUTH_API_KEY = getattr(settings, "DJ_OTTU_AUTH_API_KEY", "")

# `KeyCloakAuth`
AUTH_KEYCLOAK_USERNAME = getattr(settings, "DJ_OTTU_AUTH_KEYCLOAK_USERNAME", "")
AUTH_KEYCLOAK_PASSWORD = getattr(settings, "DJ_OTTU_AUTH_KEYCLOAK_PASSWORD", "")
AUTH_KEYCLOAK_HOST = getattr(settings, "DJ_OTTU_AUTH_KEYCLOAK_HOST", "")
AUTH_KEYCLOAK_REALM = getattr(settings, "DJ_OTTU_AUTH_KEYCLOAK_REALM", "")
AUTH_KEYCLOAK_CLIENT_ID = getattr(settings, "DJ_OTTU_AUTH_KEYCLOAK_CLIENT_ID", "")

ABSTRACT_CHECKOUT_MODEL = getattr(settings, "DJ_OTTU_ABSTRACT_CHECKOUT_MODEL", False)
ABSTRACT_WEBHOOK_MODEL = getattr(settings, "DJ_OTTU_ABSTRACT_WEBHOOK_MODEL", False)
WEBHOOK_KEY = getattr(settings, "DJ_OTTU_WEBHOOK_KEY", "")
WEBHOOK_URL = getattr(settings, "DJ_OTTU_WEBHOOK_URL", "")

# Validation
auth_basic = AUTH_USERNAME and AUTH_PASSWORD
auth_api_key = AUTH_API_KEY
auth_keycloak = (
    AUTH_KEYCLOAK_USERNAME
    and AUTH_KEYCLOAK_PASSWORD
    and AUTH_KEYCLOAK_HOST
    and AUTH_KEYCLOAK_REALM
    and AUTH_KEYCLOAK_CLIENT_ID
)

if not (auth_basic or auth_api_key or auth_keycloak):
    raise ConfigurationError("Missing authentication credentials")
