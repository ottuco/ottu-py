from __future__ import annotations

import hashlib
import hmac
import time
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime
from typing import Any

# The 18 flat top-level fields covered by the body ``signature``:
# ``key+value`` concatenation, no delimiter, sorted by field name.
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


def _hmac_digest(message: str, key: str) -> str:
    # surrogatepass: a lone surrogate from untrusted JSON (json.loads('"\\ud800"'))
    # must not raise. It encodes to bytes no valid string produces, so two
    # different messages still never share a digest.
    return hmac.new(
        key.encode("utf8"),
        message.encode("utf8", "surrogatepass"),
        digestmod=hashlib.sha256,
    ).hexdigest()


def verify_signature(
    payload: dict,
    signature: str,
    webhook_key: str,
) -> bool:
    # Body ``signature``: the documented 18-field recipe only. Everything else in the
    # body is covered by the Ottu-Signature header (verify_ottu_signature_raw).
    # Accepting a wider recipe here would let an 18-field signature stand in for
    # fields it never covered.
    # An empty key lets anyone mint a valid HMAC; a non-str key raises in key.encode.
    if not isinstance(webhook_key, str) or not webhook_key:
        return False
    # ``signature`` is untrusted JSON; compare_digest raises on non-ASCII str / non-str.
    if not isinstance(signature, str) or not signature.isascii():
        return False
    expected = calculate_hmac_signature(payload=payload, hmac_key=webhook_key)
    return hmac.compare_digest(expected, signature)


def verify_ottu_signature_raw(
    body: bytes,
    header: str | None,
    webhook_key: str,
    *,
    tolerance_seconds: int | None = 300,
) -> bool:
    """Verify the ``Ottu-Signature: t=<unix_seconds>,v2=<hex>`` webhook header (v2).

    ``v2`` is HMAC-SHA256 over ``f"{t}."`` followed by the exact bytes that were
    POSTed. Pass the raw request body (``request.body``), never a parsed and
    re-serialized payload: any other bytes fail.

    Returns ``False`` for every failure and never raises on header or body
    input: a non-``bytes`` body, a missing or malformed header, no ``v2`` pair,
    bad ``t``, ``t`` further than ``tolerance_seconds`` from now (either
    direction; ``None`` disables the check), or an HMAC mismatch. Other header
    versions (``v3``...) are ignored. An empty or non-str ``webhook_key`` also
    returns ``False``: an empty key lets anyone mint a valid HMAC.
    """
    if not isinstance(webhook_key, str) or not webhook_key:
        return False
    if not isinstance(body, bytes) or not isinstance(header, str):
        return False
    pairs: dict[str, str] = {}
    for item in header.split(","):
        key, sep, value = item.partition("=")
        if sep:
            pairs[key.strip()] = value.strip()
    t, received = pairs.get("t", ""), pairs.get("v2", "")
    # isdigit() alone accepts "²", then int() raises. Unix seconds have 10 digits
    # today; capping at 12 keeps int() and the float math below from raising on a
    # crafted header.
    if not (t.isascii() and t.isdigit() and len(t) <= 12):
        return False
    if not received.isascii():
        return False
    if tolerance_seconds is not None and abs(time.time() - int(t)) > tolerance_seconds:
        return False
    # ``t`` goes in exactly as received: it is the text Ottu signed.
    expected = hmac.new(
        webhook_key.encode("utf8"), f"{t}.".encode() + body, hashlib.sha256
    ).hexdigest()
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


class InvalidOttuEvent(ValueError):
    """The body is not a v3 webhook event envelope."""


@dataclass
class OttuEvent:
    """A Connect v3 webhook event envelope.

    Verify the ``Ottu-Signature`` header with :func:`verify_ottu_signature_raw`
    first; this reader trusts nothing and checks the envelope shape only.
    ``type`` is any string: new event types arrive without a new ottu-py release.
    ``data`` is the resource dict as sent (``payment``, ``operation``...).
    ``id`` is the same on every retry of one event: deduplicate on it.
    """

    id: str
    type: str
    created: datetime
    version: int
    is_sandbox: bool
    merchant_id: str
    data: dict[str, Any]

    @classmethod
    def from_dict(cls, raw: Mapping[str, Any]) -> OttuEvent:
        """Build an event from the parsed JSON body.

        Raises :class:`InvalidOttuEvent` if the body is not a v3 envelope.
        """
        if not isinstance(raw, Mapping):
            raise InvalidOttuEvent("event must be a JSON object")
        version = raw.get("version")
        # bool is an int subclass: a JSON `true` must not pass as version 3.
        if type(version) is not int or version != 3:
            raise InvalidOttuEvent(f"version must be 3, got {version!r}")
        for name in ("id", "type", "merchant_id"):
            value = raw.get(name)
            # A blank id would make every such event share one dedupe key.
            if not isinstance(value, str) or not value.strip():
                raise InvalidOttuEvent(f"{name} must be a non-empty string")
        if not isinstance(raw.get("is_sandbox"), bool):
            raise InvalidOttuEvent("is_sandbox must be a boolean")
        if not isinstance(raw.get("data"), dict):
            raise InvalidOttuEvent("data must be a JSON object")
        return cls(
            id=raw["id"],
            type=raw["type"],
            created=_parse_created(raw.get("created")),
            version=3,
            is_sandbox=raw["is_sandbox"],
            merchant_id=raw["merchant_id"],
            data=raw["data"],
        )


def _parse_created(value: object) -> datetime:
    if not isinstance(value, str):
        raise InvalidOttuEvent("created must be an ISO 8601 string")
    try:
        # Python 3.10's fromisoformat rejects a trailing "Z"; 3.11+ accepts it.
        iso = value[:-1] + "+00:00" if value.endswith("Z") else value
        created = datetime.fromisoformat(iso)
    except ValueError as exc:
        raise InvalidOttuEvent(f"created is not ISO 8601: {value!r}") from exc
    if created.tzinfo is None:
        raise InvalidOttuEvent("created must carry a UTC offset")
    return created
