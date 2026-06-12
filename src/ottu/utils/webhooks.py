from __future__ import annotations

import hashlib
import hmac

# Standard 18 flat top-level fields — the default signing contract used by all
# Ottu merchants. ``key+value`` concatenation, no delimiter, sorted by field name.
# Mirrors core_backend ``utils/signing.py:sign_merchant_payload`` pre-feat/153560.
_SIGNED_FIELDS = [
    "amount",
    "currency_code",
    "customer_address_city",
    "customer_address_country",
    "customer_address_line1",
    "customer_address_line2",
    "customer_address_postal_code",
    "customer_address_state",
    "customer_email",
    "customer_first_name",
    "customer_last_name",
    "customer_phone",
    "gateway_account",
    "gateway_name",
    "order_no",
    "reference_number",
    "result",
    "state",
]

# Extended 26-field set for subscription/autopay webhooks (Connect feat/153560+).
# Exactly _SIGNED_FIELDS + 8 subscription-specific nested paths covering token,
# agreement, and extra autopay metadata. ``path=value`` joined by ``\n``.
_SUBSCRIPTION_SIGNED_FIELDS = sorted(
    _SIGNED_FIELDS
    + [
        "agreement.id",
        "extra.autopay.subscription_id",
        "extra.merchant_id",
        "payment_type",
        "session_id",
        "token.customer_id",
        "token.pg_code",
        "token.token",
    ]
)

_MISSING = object()


def _hmac_digest(message: str, key: str) -> str:
    return hmac.new(
        key.encode("utf8"),
        message.encode("utf8"),
        digestmod=hashlib.sha256,
    ).hexdigest()


def _resolve_path(payload: dict, path: str) -> object:
    current: object = payload
    for part in path.split("."):
        if not isinstance(current, dict) or part not in current:
            return _MISSING
        current = current[part]
    return current


def verify_signature(
    payload: dict,
    signature: str,
    webhook_key: str,
) -> bool:
    # Standard 18-field verification first — covers all regular merchants.
    # Falls back to the subscription 26-field algorithm for betabulk and any
    # Ottu instance that has shipped feat/153560 (autopay/subscription webhooks).
    std_sig = calculate_hmac_signature(payload=payload, hmac_key=webhook_key)
    if hmac.compare_digest(std_sig, signature):
        return True
    sub_sig = calculate_subscription_hmac_signature(payload=payload, hmac_key=webhook_key)
    return hmac.compare_digest(sub_sig, signature)


def calculate_hmac_signature(payload: dict, hmac_key: str) -> str:
    # Standard algorithm: 18 flat top-level fields, ``key+value`` concatenation,
    # no delimiter. Default for all merchants.
    parts = [
        f"{k}{payload[k]}"
        for k in sorted(_SIGNED_FIELDS)
        if k in payload and payload[k] is not None and payload[k] != ""
    ]
    message = "".join(parts)
    return _hmac_digest(message, hmac_key)


def calculate_subscription_hmac_signature(payload: dict, hmac_key: str) -> str:
    # Subscription/autopay algorithm: 26 fields including nested dotted paths
    # (token.*, agreement.id, extra.*). ``path=value`` joined by ``\n``.
    # Used by Connect feat/153560+ for autopay webhook verification.
    parts: list[str] = []
    for path in _SUBSCRIPTION_SIGNED_FIELDS:
        value = _resolve_path(payload, path)
        if value is _MISSING or value is None or value == "":
            continue
        parts.append(f"{path}={value}")
    message = "\n".join(parts)
    return _hmac_digest(message, hmac_key)
