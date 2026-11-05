from __future__ import annotations

import hashlib
import hmac
import time
from collections.abc import Mapping
from dataclasses import dataclass, fields
from datetime import datetime
from typing import Any, TypeVar

_T = TypeVar("_T")

__all__ = [
    "verify_signature",
    "verify_ottu_signature_raw",
    "calculate_hmac_signature",
    "InvalidOttuEvent",
    "OttuEvent",
    "Actor",
    "PaymentCard",
    "Connector",
    "Totals",
    "PaymentEvent",
    "SubscriptionObject",
    "Cancellation",
]

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


def _mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _build(cls: type[_T], raw: object, **nested: Any) -> _T:
    """`cls` from a JSON object: each field reads its own key, missing keys are None.

    `data` content is never validated: #160599 R7 lets Connect add fields, and a
    typed view must not break on a key it does not know or a key it expected and
    did not get.
    """
    source = _mapping(raw)
    values = {f.name: source.get(f.name) for f in fields(cls)}  # type: ignore[arg-type]
    values.update(nested)
    return cls(**values)


@dataclass
class Actor:
    """Who caused an event (#160599 R3). Keys that do not apply are None."""

    kind: Any
    id: Any
    first_name: Any
    last_name: Any
    email: Any


@dataclass
class PaymentCard:
    """The card of an attempt or the card on file (#160599 R5)."""

    number: Any
    brand: Any
    scheme: Any
    bin: Any
    expiry_month: Any
    expiry_year: Any
    name_on_card: Any
    token: Any
    cvv_required: Any
    is_preferred: Any
    agreements: Any


@dataclass
class Connector:
    """The gateway part of a payment event (#160599 R5).

    Money is in the gateway currency.
    """

    code: Any
    identifier: Any
    processor: Any
    reference_number: Any
    currency: Any
    amount: Any
    exchange_rate: Any
    fee: Any
    total: Any
    params: Any
    responses: Any


@dataclass
class Totals:
    """Running totals in the session currency, fees excluded (#160599 R5)."""

    paid: Any
    settled: Any
    refunded: Any
    refund_pending: Any
    voided: Any
    remaining: Any


@dataclass
class PaymentEvent:
    """``data`` of a ``payment.*`` event (#160599 R5).

    Money and timestamps are strings, as sent.
    """

    session_id: Any
    order_no: Any
    payment_type: Any
    language: Any
    amount: Any
    currency: Any
    status: Any
    operation: Any
    processed_at: Any
    result: Any
    message: Any
    channel: Any
    form_of_payment: Any
    card: PaymentCard
    connector: Connector
    totals: Totals
    customer: Any
    billing_address: Any
    shipping_address: Any
    agreement: Any
    wallets: Any
    extra: Any
    created_by: Actor
    created_at: Any
    updated_at: Any

    @classmethod
    def from_dict(cls, raw: object) -> PaymentEvent:
        source = _mapping(raw)
        return _build(
            cls,
            source,
            card=_build(PaymentCard, source.get("card")),
            connector=_build(Connector, source.get("connector")),
            totals=_build(Totals, source.get("totals")),
            created_by=_build(Actor, source.get("created_by")),
        )


@dataclass
class Cancellation:
    """The cancellation part of a subscription (#160607 R3).

    ``canceled_by`` is an :class:`Actor`: one shape wherever a who appears (#160599 R3).
    """

    at_period_end: Any
    cancel_date: Any
    canceled_at: Any
    canceled_by: Actor
    reason: Any
    note: Any


@dataclass
class SubscriptionObject:
    """``data`` of a ``subscription.*`` event (AutoPay, #160607 R3)."""

    subscription_id: Any
    status: Any
    order_no: Any
    plan_name: Any
    description: Any
    language: Any
    amount: Any
    first_payment_amount: Any
    currency: Any
    billing_anchor_day: Any
    retry_count: Any
    start_date: Any
    end_date: Any
    next_billing_date: Any
    customer: Any
    card: PaymentCard
    agreement: Any
    cancellation: Cancellation
    setup_session_id: Any
    latest_session_id: Any
    created_by: Actor
    created_at: Any
    updated_at: Any
    status_changed_at: Any

    @classmethod
    def from_dict(cls, raw: object) -> SubscriptionObject:
        source = _mapping(raw)
        cancellation = source.get("cancellation")
        return _build(
            cls,
            source,
            card=_build(PaymentCard, source.get("card")),
            cancellation=_build(
                Cancellation,
                cancellation,
                canceled_by=_build(Actor, _mapping(cancellation).get("canceled_by")),
            ),
            created_by=_build(Actor, source.get("created_by")),
        )


@dataclass
class OttuEvent:
    """A Connect v3 webhook event envelope (#160599 R2).

    Verify the ``Ottu-Signature`` header with :func:`verify_ottu_signature_raw`
    first; this reader trusts nothing and checks the envelope shape only.
    ``event`` is any string: new events arrive without a new ottu-py release.
    ``data`` is the object itself, as sent. Use :attr:`payment` or
    :attr:`subscription` for typed access.
    ``id`` is the same on every retry of one event: deduplicate on it.
    """

    id: str
    event: str
    created: datetime
    version: int
    is_sandbox: bool
    merchant_id: str
    initiator: Actor
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
        for name in ("id", "event", "merchant_id"):
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
            event=raw["event"],
            created=_parse_created(raw.get("created")),
            version=3,
            is_sandbox=raw["is_sandbox"],
            merchant_id=raw["merchant_id"],
            initiator=_build(Actor, raw.get("initiator")),
            data=raw["data"],
        )

    @property
    def payment(self) -> PaymentEvent | None:
        """Typed ``data`` of a ``payment.*`` event, else None."""
        if not self.event.startswith("payment."):
            return None
        return PaymentEvent.from_dict(self.data)

    @property
    def subscription(self) -> SubscriptionObject | None:
        """Typed ``data`` of a ``subscription.*`` event, else None."""
        if not self.event.startswith("subscription."):
            return None
        return SubscriptionObject.from_dict(self.data)


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
