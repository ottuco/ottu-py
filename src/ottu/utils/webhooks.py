from __future__ import annotations

import hashlib
import hmac
import time

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

# Ottu-Signature v1 field set: _SIGNED_FIELDS + 8 nested/extra dotted paths
# (token, agreement, extra autopay metadata). Signed in the ``Ottu-Signature``
# header, never in the body ``signature``. FROZEN: every merchant verifier signs
# exactly this set, so any change to it is v2, never an edit of v1.
_V1_SIGNED_FIELDS = sorted(
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
_MAX_T_DIGITS = 12


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


def _v1_message(payload: dict, t: str) -> str | None:
    # ``t`` goes in exactly as received. A signed value that is not a string makes
    # the whole check fail: Connect emits strings only, and languages render
    # True / 1.0 differently, so rendering them would let verifiers disagree.
    lines = [f"t={t}"]
    for path in _V1_SIGNED_FIELDS:
        value = _resolve_path(payload, path)
        if value is _MISSING or value is None or value == "":
            continue
        if not isinstance(value, str):
            return None
        lines.append(f"{path}={value}")
    return "\n".join(lines)


def verify_signature(
    payload: dict,
    signature: str,
    webhook_key: str,
) -> bool:
    # Body ``signature``: the documented 18-field recipe only. The extended set is
    # verified from the Ottu-Signature header (verify_ottu_signature). Accepting
    # it here too would let an 18-field signature stand in for fields it never covered.
    # ``signature`` is untrusted JSON; compare_digest raises on non-ASCII str / non-str.
    if not isinstance(signature, str) or not signature.isascii():
        return False
    expected = calculate_hmac_signature(payload=payload, hmac_key=webhook_key)
    return hmac.compare_digest(expected, signature)


def verify_ottu_signature(
    payload: dict,
    header: str | None,
    webhook_key: str,
    *,
    tolerance_seconds: int | None = 300,
) -> bool:
    """Verify the ``Ottu-Signature: t=<unix_seconds>,v1=<hex>`` webhook header (v1).

    Returns ``False`` for every failure and never raises: missing or malformed
    header, bad ``t``, ``t`` further than ``tolerance_seconds`` from now (either
    direction; ``None`` disables the check), non-string signed value, or HMAC
    mismatch. Unknown header keys (``v2``...) are ignored.
    """
    if not isinstance(header, str):
        return False
    pairs: dict[str, str] = {}
    for item in header.split(","):
        key, sep, value = item.partition("=")
        if sep:
            pairs[key.strip()] = value.strip()
    t, received = pairs.get("t", ""), pairs.get("v1", "")
    # isdigit() alone accepts "²", then int() raises. The length cap keeps int() and
    # the float math below from raising on a crafted header (unix seconds: 10 digits).
    if not (t.isascii() and t.isdigit() and len(t) <= _MAX_T_DIGITS):
        return False
    if not received or not received.isascii():
        return False
    if tolerance_seconds is not None and abs(time.time() - int(t)) > tolerance_seconds:
        return False
    message = _v1_message(payload, t)
    if message is None:
        return False
    try:
        expected = _hmac_digest(message, webhook_key)
    except UnicodeEncodeError:  # lone surrogate in a value from untrusted JSON
        return False
    return hmac.compare_digest(expected, received)


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
