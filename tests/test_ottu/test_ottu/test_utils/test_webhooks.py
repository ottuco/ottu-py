import copy
import hashlib
import hmac
import json
from datetime import datetime, timezone
from types import SimpleNamespace

import pytest

from ottu.utils import webhooks
from ottu.utils.webhooks import (
    _SIGNED_FIELDS,
    Actor,
    Cancellation,
    Connector,
    InvalidOttuEvent,
    OttuEvent,
    PaymentCard,
    SubscriptionObject,
    Totals,
    calculate_hmac_signature,
    verify_ottu_signature_raw,
    verify_signature,
)
from tests.fake_data import (
    SIGNED_PAYLOAD,
    SIGNED_PAYLOAD_EXTENDED_SIGNATURE,
    SIGNED_PAYLOAD_SIGNATURE,
    V2_PAYMENT_BODY,
    V2_PAYMENT_HEADER,
    V2_PAYMENT_SIGNATURE,
    V2_UNICODE_BODY,
    V2_UNICODE_HEADER,
    V3_EVENT,
    WEBHOOK_KEY,
    WEBHOOK_TIMESTAMP,
)

KEY = "test-key"

# The shared vectors (WEBHOOK_*, SIGNED_PAYLOAD*, V2_*) are pinned hex literals
# in tests/fake_data.py.

DOCS_3_FIELD_PAYLOAD = {
    "amount": "86.000",
    "currency_code": "KWD",
    "customer_first_name": "example-customer",
}
DOCS_3_FIELD_HEX = "6143b8ad4bd283540721ab000f6de746e722231aaaa90bc38f639081d3ff9f67"

# Live docs example (docs.ottu.com/developers/webhooks/verify-signatures,
# fetched 2026-10-21): 12 keys, one of them empty.
DOCS_LIVE_PAYLOAD = {
    "amount": "86.000",
    "currency_code": "KWD",
    "customer_first_name": "example-customer",
    "customer_last_name": "",
    "customer_email": "customer@example.com",
    "gateway_name": "kpay",
    "gateway_account": "knet",
    "order_no": "ORDER-1001",
    "reference_number": "ABC12",
    "result": "success",
    "session_id": "a12f71075a834a34d692736ac43a212fcebfb6ec",
    "state": "paid",
}
DOCS_LIVE_HEX = "29e70de083707b3a738e9d5f4df4e4481d082c4614db97a55f50d4b4583dc5f2"

# HMAC-SHA256 with the EMPTY key "" over the same messages (stdlib, computed once and
# pinned). An attacker who knows the key is empty can mint these, so the verifiers
# must refuse an unusable key instead of accepting them.
EMPTY_KEY_BODY_HEX = "8ed6d363ce08ea3eff22cc32cf7007fcbceb45208ffb8a9f132c5db32e6adec9"
# ... over f"{WEBHOOK_TIMESTAMP}." + V2_PAYMENT_BODY.
EMPTY_KEY_V2_HEX = "4ec16fbf83792b3e546512ab69465a9753a149023b763f6f2556eae35e0c3266"

V2_VECTORS = [
    pytest.param(V2_UNICODE_BODY, V2_UNICODE_HEADER, id="unicode-body"),
    pytest.param(V2_PAYMENT_BODY, V2_PAYMENT_HEADER, id="536-byte-payload"),
]


# ---------------------------------------------------------------------------
# Standard (18-field) test fixtures
# ---------------------------------------------------------------------------

# Flat payload representative of a standard merchant webhook (no nested fields).
_STD_PAYLOAD = {
    "amount": "50.000",
    "currency_code": "KWD",
    "gateway_name": "knet",
    "gateway_account": "default",
    "order_no": "ord-1",
    "reference_number": "ref-1",
    "result": "success",
    "state": "paid",
    # Fields present in real payloads but NOT in the standard signed set.
    "customer_id": "cust-top",
    "session_id": "sess-1",
}
# Canonical form: sorted(_SIGNED_FIELDS) keys present in payload, key+value,
# no delimiter.
_STD_MESSAGE = (
    "amount50.000"
    "currency_codeKWD"
    "gateway_accountdefault"
    "gateway_nameknet"
    "order_noord-1"
    "reference_numberref-1"
    "resultsuccess"
    "statepaid"
)


def _digest(message: str) -> str:
    return hmac.new(
        KEY.encode("utf8"), message.encode("utf8"), hashlib.sha256
    ).hexdigest()


def _set_path(payload: dict, path: str, value: object) -> dict:
    out = copy.deepcopy(payload)
    parts = path.split(".")
    current = out
    for part in parts[:-1]:
        current = current.setdefault(part, {})
    current[parts[-1]] = value
    return out


def _verify_v2(body: bytes, header: object = V2_PAYMENT_HEADER, **kwargs) -> bool:
    # The shared vectors carry t=1792417440, which is stale against the real clock,
    # so most cases switch the age check off. The age check has its own tests.
    kwargs.setdefault("tolerance_seconds", None)
    # header may be None, bytes or int here: the cases that must return False
    return verify_ottu_signature_raw(
        body, header, WEBHOOK_KEY, **kwargs  # type: ignore[arg-type]
    )


# ---------------------------------------------------------------------------
# Field set tests
# ---------------------------------------------------------------------------


class TestStandardSignedFields:
    def test_exactly_18_fields(self):
        assert len(_SIGNED_FIELDS) == 18

    def test_all_flat_keys(self):
        assert all("." not in f for f in _SIGNED_FIELDS)


# ---------------------------------------------------------------------------
# Standard 18-field algorithm
# ---------------------------------------------------------------------------


class TestStandardSignature:
    def test_canonical_message(self):
        assert calculate_hmac_signature(_STD_PAYLOAD, KEY) == _digest(_STD_MESSAGE)

    def test_unsigned_fields_excluded(self):
        # customer_id and session_id are not in _SIGNED_FIELDS.
        without = calculate_hmac_signature(_STD_PAYLOAD, KEY)
        extra = {
            **_STD_PAYLOAD,
            "customer_id": "someone-else",
            "session_id": "hijacked",
        }
        assert calculate_hmac_signature(extra, KEY) == without

    def test_empty_field_skipped(self):
        with_empty = calculate_hmac_signature({**_STD_PAYLOAD, "state": ""}, KEY)
        without_state = calculate_hmac_signature(
            {k: v for k, v in _STD_PAYLOAD.items() if k != "state"}, KEY
        )
        assert with_empty == without_state

    def test_zero_string_not_skipped(self):
        # "0" is a valid non-empty string — must be included, not treated as absent.
        with_zero = calculate_hmac_signature({**_STD_PAYLOAD, "amount": "0"}, KEY)
        without_amount = calculate_hmac_signature(
            {k: v for k, v in _STD_PAYLOAD.items() if k != "amount"}, KEY
        )
        assert with_zero != without_amount

    def test_null_field_skipped(self):
        # None is treated as absent — same result as the field not being in the payload.
        with_null = calculate_hmac_signature({**_STD_PAYLOAD, "state": None}, KEY)
        without_state = calculate_hmac_signature(
            {k: v for k, v in _STD_PAYLOAD.items() if k != "state"}, KEY
        )
        assert with_null == without_state

    def test_missing_fields_produce_empty_message(self):
        assert calculate_hmac_signature({}, KEY) == _digest("")

    def test_produces_64_char_hex(self):
        sig = calculate_hmac_signature(_STD_PAYLOAD, KEY)
        assert isinstance(sig, str) and len(sig) == 64


# ---------------------------------------------------------------------------
# verify_signature — documented 18-field body recipe only
# ---------------------------------------------------------------------------


class TestVerifySignature:
    def test_accepts_ticket_body_vector(self):
        assert (
            verify_signature(SIGNED_PAYLOAD, SIGNED_PAYLOAD_SIGNATURE, WEBHOOK_KEY)
            is True
        )

    def test_accepts_docs_3_field_example(self):
        assert (
            verify_signature(DOCS_3_FIELD_PAYLOAD, DOCS_3_FIELD_HEX, WEBHOOK_KEY)
            is True
        )

    def test_accepts_live_docs_example(self):
        assert verify_signature(DOCS_LIVE_PAYLOAD, DOCS_LIVE_HEX, WEBHOOK_KEY) is True

    def test_rejects_26_field_body_signature(self):
        # A body signature must never be accepted for the extended 26-field set.
        # The signature below is the 26-field recipe over SIGNED_PAYLOAD.
        assert (
            verify_signature(
                SIGNED_PAYLOAD, SIGNED_PAYLOAD_EXTENDED_SIGNATURE, WEBHOOK_KEY
            )
            is False
        )

    def test_rejects_v2_header_hex_as_body_signature(self):
        assert (
            verify_signature(SIGNED_PAYLOAD, V2_PAYMENT_SIGNATURE, WEBHOOK_KEY) is False
        )

    def test_rejects_tampered_payload(self):
        tampered = _set_path(SIGNED_PAYLOAD, "amount", "999.000")
        assert (
            verify_signature(tampered, SIGNED_PAYLOAD_SIGNATURE, WEBHOOK_KEY) is False
        )

    def test_rejects_wrong_key(self):
        assert (
            verify_signature(SIGNED_PAYLOAD, SIGNED_PAYLOAD_SIGNATURE, "wrong-key")
            is False
        )

    @pytest.mark.parametrize("key", ["", None, b"key"], ids=["empty", "none", "bytes"])
    def test_unusable_webhook_key_false(self, key):
        # With key "" the signature below is valid HMAC math, so only the key
        # check stops it. None and bytes would raise without the check.
        assert verify_signature(SIGNED_PAYLOAD, EMPTY_KEY_BODY_HEX, key) is False

    @pytest.mark.parametrize(
        "signature",
        [
            None,
            "",
            "é",
            SIGNED_PAYLOAD_SIGNATURE.replace("b", "é", 1),
            123,
            b"bb0e1db6",
        ],
        ids=["none", "empty", "non-ascii", "non-ascii-in-hex", "int", "bytes"],
    )
    def test_rejects_bad_signature_without_raising(self, signature):
        # `signature` comes from untrusted JSON. It must return False, never raise.
        assert verify_signature(SIGNED_PAYLOAD, signature, WEBHOOK_KEY) is False

    @pytest.mark.parametrize("path", ["reference_number", "customer_first_name"])
    def test_lone_surrogate_in_signed_value_false(self, path):
        # json.loads('"\\ud800"') yields a str that cannot be UTF-8 encoded.
        # Must be False, never raise.
        changed = _set_path(SIGNED_PAYLOAD, path, SIGNED_PAYLOAD[path] + "\ud800")
        assert verify_signature(changed, SIGNED_PAYLOAD_SIGNATURE, WEBHOOK_KEY) is False


# ---------------------------------------------------------------------------
# verify_ottu_signature_raw — Ottu-Signature header, v2 (HMAC over t. + raw body)
# ---------------------------------------------------------------------------


class TestVerifyOttuSignatureRaw:
    @pytest.mark.parametrize(("body", "header"), V2_VECTORS)
    def test_ticket_vector_true(self, body, header):
        assert _verify_v2(body, header) is True

    def test_vector_2_is_the_536_byte_ticket_payload(self):
        # Guards the pinned bytes against an accidental edit, and ties the v2 body
        # to the payload the body-signature vector uses.
        assert len(V2_PAYMENT_BODY) == 536
        assert json.loads(V2_PAYMENT_BODY) == SIGNED_PAYLOAD

    @pytest.mark.parametrize(
        "body",
        [
            V2_PAYMENT_BODY.replace(b"86.000", b"86.001"),
            V2_PAYMENT_BODY.replace(b"6c2a1f0e9b", b"6c2a1f0e9c"),
            V2_PAYMENT_BODY.replace(b"9923965822244314", b"9923965822244315"),
            V2_PAYMENT_BODY + b" ",
            V2_PAYMENT_BODY + b"\n",
            V2_PAYMENT_BODY[:-1],
            b"",
        ],
        ids=[
            "amount",
            "session-id",
            "token",
            "trailing-space",
            "trailing-newline",
            "truncated",
            "empty",
        ],
    )
    def test_one_byte_change_in_body_false(self, body):
        assert _verify_v2(body) is False

    @pytest.mark.parametrize(("body", "header"), V2_VECTORS)
    def test_reserialized_body_false(self, body, header):
        # The signature covers the bytes Ottu sent. A parsed and re-dumped body
        # has the same data but other bytes (spaces, \u escapes), so it must fail.
        reserialized = json.dumps(json.loads(body)).encode("utf-8")
        assert reserialized != body
        assert _verify_v2(reserialized, header) is False

    def test_whitespace_around_pairs_is_stripped(self):
        header = f"t={WEBHOOK_TIMESTAMP}, v2={V2_PAYMENT_SIGNATURE}"
        assert _verify_v2(V2_PAYMENT_BODY, header) is True
        header = f" t={WEBHOOK_TIMESTAMP} ,  v2={V2_PAYMENT_SIGNATURE} "
        assert _verify_v2(V2_PAYMENT_BODY, header) is True

    def test_pair_order_does_not_matter(self):
        header = f"v2={V2_PAYMENT_SIGNATURE},t={WEBHOOK_TIMESTAMP}"
        assert _verify_v2(V2_PAYMENT_BODY, header) is True

    @pytest.mark.parametrize(
        "header",
        [
            f"t={WEBHOOK_TIMESTAMP},v2={V2_PAYMENT_SIGNATURE},v3=deadbeef",
            f"v3=deadbeef,t={WEBHOOK_TIMESTAMP},v2={V2_PAYMENT_SIGNATURE}",
            f"t={WEBHOOK_TIMESTAMP},v1={'0' * 64},"
            f"v2={V2_PAYMENT_SIGNATURE},future=1,v4=",
        ],
    )
    def test_unknown_versions_ignored(self, header):
        # A verifier picks the version it knows and ignores the rest.
        assert _verify_v2(V2_PAYMENT_BODY, header) is True

    def test_t_changed_false(self):
        header = f"t={WEBHOOK_TIMESTAMP + 1},v2={V2_PAYMENT_SIGNATURE}"
        assert _verify_v2(V2_PAYMENT_BODY, header) is False

    def test_t_is_signed_exactly_as_received(self):
        # int("01792417440") == WEBHOOK_TIMESTAMP,
        # but the signed prefix is "01792417440.".
        header = f"t=0{WEBHOOK_TIMESTAMP},v2={V2_PAYMENT_SIGNATURE}"
        assert _verify_v2(V2_PAYMENT_BODY, header) is False

    @pytest.mark.parametrize(
        "header",
        [
            None,
            "",
            "   ",
            "garbage",
            f"t={WEBHOOK_TIMESTAMP}",
            f"v2={V2_PAYMENT_SIGNATURE}",
            f"t=,v2={V2_PAYMENT_SIGNATURE}",
            f"t={WEBHOOK_TIMESTAMP},v2=",
            f"t=abc,v2={V2_PAYMENT_SIGNATURE}",
            f"t=-{WEBHOOK_TIMESTAMP},v2={V2_PAYMENT_SIGNATURE}",
            f"t=1.5,v2={V2_PAYMENT_SIGNATURE}",
            f"t=²,v2={V2_PAYMENT_SIGNATURE}",  # str.isdigit() is True, int() raises
            f"t=١٢,v2={V2_PAYMENT_SIGNATURE}",  # Arabic-Indic: int() accepts
            # hmac.compare_digest raises on non-ASCII str
            f"t={WEBHOOK_TIMESTAMP},v2=é",
            # lowercase only
            f"t={WEBHOOK_TIMESTAMP},v2={V2_PAYMENT_SIGNATURE.upper()}",
            f"t={WEBHOOK_TIMESTAMP},v1={V2_PAYMENT_SIGNATURE}",  # no header v1 exists
            f"t={WEBHOOK_TIMESTAMP},v3={V2_PAYMENT_SIGNATURE}",
            f"t={WEBHOOK_TIMESTAMP},v2={V2_PAYMENT_SIGNATURE[:-1]}",
            f"t={WEBHOOK_TIMESTAMP},v2={'0' * 64}",
            ",,,",
            "=,=",
            b"t=1792417440,v2=9ccd4a02",
            12345,
        ],
        ids=[
            "none",
            "empty",
            "blank",
            "garbage",
            "t-only",
            "v2-only",
            "t-empty",
            "v2-empty",
            "t-alpha",
            "t-negative",
            "t-float",
            "t-superscript-two",
            "t-arabic-digits",
            "v2-non-ascii",
            "v2-uppercase",
            "v1-only",
            "v3-only",
            "v2-truncated",
            "v2-zeros",
            "commas-only",
            "equals-only",
            "bytes",
            "int",
        ],
    )
    def test_header_missing_or_malformed_false(self, header):
        assert _verify_v2(V2_PAYMENT_BODY, header) is False
        # The default tolerance runs int(t); a malformed t must not reach it.
        assert verify_ottu_signature_raw(V2_PAYMENT_BODY, header, WEBHOOK_KEY) is False

    @pytest.mark.parametrize("digits", [13, 400, 5000])
    def test_oversized_t_false_without_raising(self, digits):
        # int() raises ValueError past 4300 digits (3.10.7+) and float() math raises
        # OverflowError past ~308 digits. Unix seconds never need more than 12.
        header = f"t={'9' * digits},v2={V2_PAYMENT_SIGNATURE}"
        assert _verify_v2(V2_PAYMENT_BODY, header) is False
        assert verify_ottu_signature_raw(V2_PAYMENT_BODY, header, WEBHOOK_KEY) is False

    @pytest.mark.parametrize(
        "body",
        [None, "not-bytes", V2_PAYMENT_BODY.decode(), {"amount": "86.000"}, 7],
        ids=["none", "str", "decoded-vector", "dict", "int"],
    )
    def test_non_bytes_body_false(self, body):
        # A str or dict is not "the exact bytes POSTed". It must not raise.
        assert _verify_v2(body) is False  # type: ignore[arg-type]

    @pytest.mark.parametrize("key", ["", None, b"key"], ids=["empty", "none", "bytes"])
    def test_unusable_webhook_key_false(self, key):
        # With key "" the header below is valid HMAC math, so only the key check
        # stops it. None and bytes would raise without the check.
        header = f"t={WEBHOOK_TIMESTAMP},v2={EMPTY_KEY_V2_HEX}"
        assert (
            verify_ottu_signature_raw(
                V2_PAYMENT_BODY, header, key, tolerance_seconds=None
            )
            is False
        )
        assert verify_ottu_signature_raw(V2_PAYMENT_BODY, header, key) is False

    def test_wrong_key_false(self):
        assert (
            verify_ottu_signature_raw(
                V2_PAYMENT_BODY,
                V2_PAYMENT_HEADER,
                "wrong-key",
                tolerance_seconds=None,
            )
            is False
        )

    @pytest.mark.parametrize(
        "hex_",
        [SIGNED_PAYLOAD_SIGNATURE, SIGNED_PAYLOAD_EXTENDED_SIGNATURE],
        ids=["18-field", "26-field"],
    )
    def test_body_signature_hex_as_v2_false(self, hex_):
        header = f"t={WEBHOOK_TIMESTAMP},v2={hex_}"
        assert _verify_v2(V2_PAYMENT_BODY, header) is False


class TestVerifyOttuSignatureRawTolerance:
    @staticmethod
    def _set_now(monkeypatch, now: int | float) -> None:
        # Replace `time` in the module under test only. The global clock stays real.
        monkeypatch.setattr(webhooks, "time", SimpleNamespace(time=lambda: now))

    @staticmethod
    def _verify(body: bytes = V2_PAYMENT_BODY, **kwargs) -> bool:
        return verify_ottu_signature_raw(body, V2_PAYMENT_HEADER, WEBHOOK_KEY, **kwargs)

    @pytest.mark.parametrize("skew", [0, -1, 1, -299, 299, -300, 300])
    def test_inside_tolerance_true(self, monkeypatch, skew):
        self._set_now(monkeypatch, WEBHOOK_TIMESTAMP + skew)
        assert self._verify() is True

    @pytest.mark.parametrize("skew", [-301, 301, -3600, 3600])
    def test_outside_tolerance_false(self, monkeypatch, skew):
        # Past (old t, replay) and future (clock skew) are both rejected.
        self._set_now(monkeypatch, WEBHOOK_TIMESTAMP + skew)
        assert self._verify() is False

    def test_fractional_clock_boundary(self, monkeypatch):
        self._set_now(monkeypatch, WEBHOOK_TIMESTAMP + 300.4)
        assert self._verify() is False

    def test_custom_tolerance(self, monkeypatch):
        self._set_now(monkeypatch, WEBHOOK_TIMESTAMP + 60)
        assert self._verify(tolerance_seconds=60) is True
        assert self._verify(tolerance_seconds=59) is False

    def test_none_disables_age_check(self, monkeypatch):
        self._set_now(monkeypatch, WEBHOOK_TIMESTAMP + 10**9)
        assert self._verify() is False
        assert self._verify(tolerance_seconds=None) is True

    def test_tolerance_does_not_rescue_bad_signature(self, monkeypatch):
        self._set_now(monkeypatch, WEBHOOK_TIMESTAMP)
        changed = V2_PAYMENT_BODY.replace(b"6c2a1f0e9b", b"attacker00")
        assert self._verify(changed) is False


class TestConstantTimeCompare:
    # Secure SDLC rule: signatures are compared in constant time. Behaviour cannot
    # show that, so check that the comparison goes through hmac.compare_digest.
    def test_verify_signature_uses_compare_digest(self, mocker):
        spy = mocker.spy(webhooks.hmac, "compare_digest")
        assert (
            verify_signature(SIGNED_PAYLOAD, SIGNED_PAYLOAD_SIGNATURE, WEBHOOK_KEY)
            is True
        )
        spy.assert_called_once()

    def test_verify_ottu_signature_raw_uses_compare_digest(self, mocker):
        spy = mocker.spy(webhooks.hmac, "compare_digest")
        assert _verify_v2(V2_PAYMENT_BODY) is True
        spy.assert_called_once()


NO_ACTOR = Actor(kind=None, id=None, first_name=None, last_name=None, email=None)


class TestOttuEventFromDict:
    def test_parses_the_published_example(self):
        event = OttuEvent.from_dict(json.loads(json.dumps(V3_EVENT)))
        assert event == OttuEvent(
            id="evt_01JB5K2M8Q1R3T5V7X9Z0B2D4F",
            event="payment.refunded",
            created=datetime(2026, 11, 5, 8, 0, 3, tzinfo=timezone.utc),
            version=3,
            is_sandbox=False,
            merchant_id="merchant.ottu.net",
            initiator=Actor(
                kind="user",
                id=12,
                first_name="Sara",
                last_name="Ops",
                email="ops@merchant.com",
            ),
            data=V3_EVENT["data"],
        )

    def test_created_offset_parses(self):
        raw = {**V3_EVENT, "created": "2026-10-21T16:40:05+03:00"}
        assert OttuEvent.from_dict(raw).created == datetime(
            2026, 10, 21, 13, 40, 5, tzinfo=timezone.utc
        )

    def test_unknown_event_is_accepted(self):
        # New events arrive without a reader release.
        assert (
            OttuEvent.from_dict({**V3_EVENT, "event": "token.created"}).event
            == "token.created"
        )

    def test_body_with_type_and_no_event_rejected(self):
        # A 2.1.0-era envelope: `type` was renamed to `event` (#160599 R2).
        raw = {k: v for k, v in V3_EVENT.items() if k != "event"} | {
            "type": "payment.paid"
        }
        with pytest.raises(InvalidOttuEvent, match="event must be a non-empty string"):
            OttuEvent.from_dict(raw)

    @pytest.mark.parametrize("initiator", [None, "user", []])
    def test_initiator_missing_or_not_an_object_reads_as_empty_actor(self, initiator):
        raw = {**V3_EVENT, "initiator": initiator}
        assert OttuEvent.from_dict(raw).initiator == NO_ACTOR

    def test_initiator_absent_reads_as_empty_actor(self):
        raw = {k: v for k, v in V3_EVENT.items() if k != "initiator"}
        assert OttuEvent.from_dict(raw).initiator == NO_ACTOR

    @pytest.mark.parametrize(
        ("initiator", "expected"),
        [
            (
                {"kind": "system"},
                Actor(
                    kind="system", id=None, first_name=None, last_name=None, email=None
                ),
            ),
            (
                {**V3_EVENT["initiator"], "role": "x"},
                Actor(
                    kind="user",
                    id=12,
                    first_name="Sara",
                    last_name="Ops",
                    email="ops@merchant.com",
                ),
            ),
        ],
        ids=["partial-keys", "unknown-key-ignored"],
    )
    def test_initiator_partial_or_unknown_keys(self, initiator, expected):
        assert (
            OttuEvent.from_dict({**V3_EVENT, "initiator": initiator}).initiator
            == expected
        )

    def test_unknown_top_level_key_is_ignored(self):
        assert OttuEvent.from_dict({**V3_EVENT, "livemode": True}).id == V3_EVENT["id"]

    @pytest.mark.parametrize("version", [1, 2, 4, "3", 3.0, None, True])
    def test_version_not_3_rejected(self, version):
        with pytest.raises(InvalidOttuEvent, match="version"):
            OttuEvent.from_dict({**V3_EVENT, "version": version})

    def test_flat_format_2_body_rejected(self):
        # A format 1/2 body has no `version` key.
        with pytest.raises(InvalidOttuEvent, match="version"):
            OttuEvent.from_dict({**V3_EVENT["data"], "signature": "ab"})

    @pytest.mark.parametrize(
        "field",
        ["id", "event", "created", "version", "is_sandbox", "merchant_id", "data"],
    )
    def test_missing_field_rejected(self, field):
        raw = {k: v for k, v in V3_EVENT.items() if k != field}
        with pytest.raises(InvalidOttuEvent, match=field):
            OttuEvent.from_dict(raw)

    @pytest.mark.parametrize(
        ("field", "value"),
        [
            ("id", 1),
            ("event", None),
            ("merchant_id", []),
            ("is_sandbox", "false"),
            ("data", []),
            ("data", "x"),
        ],
    )
    def test_wrong_type_rejected(self, field, value):
        with pytest.raises(InvalidOttuEvent, match=field):
            OttuEvent.from_dict({**V3_EVENT, field: value})

    @pytest.mark.parametrize("field", ["id", "event", "merchant_id"])
    @pytest.mark.parametrize("value", ["", "   ", "\t\n"])
    def test_blank_strings_rejected(self, field, value):
        with pytest.raises(InvalidOttuEvent, match=field):
            OttuEvent.from_dict({**V3_EVENT, field: value})

    @pytest.mark.parametrize(
        "created", ["2026-10-21T13:40:05", "yesterday", "", 1792417440]
    )
    def test_bad_created_rejected(self, created):
        with pytest.raises(InvalidOttuEvent, match="created"):
            OttuEvent.from_dict({**V3_EVENT, "created": created})

    @pytest.mark.parametrize("raw", [[], "x", 3, None])
    def test_non_object_rejected(self, raw):
        with pytest.raises(InvalidOttuEvent, match="JSON object"):
            OttuEvent.from_dict(raw)

    def test_invalid_event_is_a_value_error(self):
        # Callers that already catch ValueError keep working.
        assert issubclass(InvalidOttuEvent, ValueError)


SUBSCRIPTION_CREATED = {
    **{k: v for k, v in V3_EVENT.items() if k not in ("event", "data", "initiator")},
    "event": "subscription.created",
    "initiator": {
        "kind": "system",
        "id": None,
        "first_name": None,
        "last_name": None,
        "email": None,
    },
    "data": {
        "subscription_id": "sub_1eQuvS6CkxA8EzDEf6nJ6uLi",
        "status": "pending_setup",
        "order_no": "INV-1042",
        "plan_name": "Gold",
        "description": None,
        "language": "en",
        "amount": "10.000",
        "first_payment_amount": "10.000",
        "currency": "KWD",
        "billing_anchor_day": 5,
        "retry_count": 3,
        "start_date": "2026-11-05",
        "end_date": None,
        "next_billing_date": None,
        "customer": {
            "id": "cus_88",
            "email": "ali@example.com",
            "first_name": "Ali",
            "last_name": "Hassan",
            "phone": None,
            "phone_2": None,
            "birthdate": None,
        },
        "card": {
            "number": None,
            "brand": None,
            "scheme": None,
            "bin": None,
            "expiry_month": None,
            "expiry_year": None,
            "name_on_card": None,
            "token": None,
            "cvv_required": None,
            "is_preferred": None,
            "agreements": [],
        },
        "agreement": {
            "id": "agr_1",
            "type": "recurring",
            "frequency": "monthly",
            "amount_variability": "fixed",
            "cycle_interval_days": 30,
            "total_cycles": None,
            "start_date": "2026-11-05",
            "expiry_date": None,
            "max_amount_per_cycle": None,
            "seller": {"name": None, "short_name": None, "category_code": None},
        },
        "cancellation": {
            "at_period_end": False,
            "cancel_date": None,
            "canceled_at": None,
            "canceled_by": {
                "kind": None,
                "id": None,
                "first_name": None,
                "last_name": None,
                "email": None,
            },
            "reason": None,
            "note": None,
        },
        "setup_session_id": "4f6c1e0b9a2d",
        "latest_session_id": "4f6c1e0b9a2d",
        "created_by": {
            "kind": "system",
            "id": None,
            "first_name": None,
            "last_name": None,
            "email": None,
        },
        "created_at": "2026-11-05T08:00:00Z",
        "updated_at": "2026-11-05T08:00:00Z",
        "status_changed_at": None,
    },
}


class TestOttuEventViews:
    def test_payment_view_reads_the_typed_fields(self):
        payment = OttuEvent.from_dict(V3_EVENT).payment
        assert payment.status == "refunded"
        assert payment.operation == "refund"
        assert payment.connector.reference_number == "R7TQ1X"
        assert payment.connector.code == "ottu-pg-live"
        assert payment.totals.refunded == "6.000"
        assert payment.card.token is None
        assert payment.created_by.kind == "api_key"
        assert payment.customer == V3_EVENT["data"]["customer"]

    def test_payment_view_is_none_for_a_subscription_event(self):
        event = OttuEvent.from_dict(SUBSCRIPTION_CREATED)
        assert event.payment is None
        assert event.subscription is not None

    def test_subscription_view_reads_the_typed_fields(self):
        sub = OttuEvent.from_dict(SUBSCRIPTION_CREATED).subscription
        assert sub == SubscriptionObject(
            **{
                **SUBSCRIPTION_CREATED["data"],
                "card": PaymentCard(**{**SUBSCRIPTION_CREATED["data"]["card"]}),
                "cancellation": Cancellation(
                    **{
                        **SUBSCRIPTION_CREATED["data"]["cancellation"],
                        "canceled_by": NO_ACTOR,
                    }
                ),
                "created_by": Actor(
                    kind="system", id=None, first_name=None, last_name=None, email=None
                ),
            }
        )

    @pytest.mark.parametrize("cancellation", [None, "x", [], "absent"])
    def test_non_object_cancellation_reads_as_empty(self, cancellation):
        data = {**SUBSCRIPTION_CREATED["data"], "cancellation": cancellation}
        if cancellation == "absent":
            del data["cancellation"]
        sub = OttuEvent.from_dict({**SUBSCRIPTION_CREATED, "data": data}).subscription
        assert sub.cancellation == Cancellation(
            at_period_end=None,
            cancel_date=None,
            canceled_at=None,
            canceled_by=NO_ACTOR,
            reason=None,
            note=None,
        )

    def test_cancellation_canceled_by_is_an_actor(self):
        canceled_by = {
            "kind": "customer",
            "id": "cus_88",
            "first_name": "Ali",
            "last_name": "Hassan",
            "email": "ali@example.com",
        }
        cancellation = {
            **SUBSCRIPTION_CREATED["data"]["cancellation"],
            "canceled_by": canceled_by,
        }
        data = {**SUBSCRIPTION_CREATED["data"], "cancellation": cancellation}
        sub = OttuEvent.from_dict({**SUBSCRIPTION_CREATED, "data": data}).subscription
        assert sub.cancellation.canceled_by == Actor(**canceled_by)
        assert isinstance(sub.cancellation.canceled_by, Actor)

    def test_neither_view_for_another_family(self):
        event = OttuEvent.from_dict(
            {**V3_EVENT, "event": "webhook.ping", "data": {"endpoint": {}}}
        )
        assert (event.payment, event.subscription) == (None, None)

    def test_null_nested_objects_read_as_empty(self):
        data = {
            **V3_EVENT["data"],
            "card": None,
            "connector": None,
            "totals": None,
            "created_by": None,
        }
        payment = OttuEvent.from_dict({**V3_EVENT, "data": data}).payment
        assert payment.card == PaymentCard(
            **{f: None for f in PaymentCard.__dataclass_fields__}
        )
        assert payment.connector == Connector(
            **{f: None for f in Connector.__dataclass_fields__}
        )
        assert payment.totals == Totals(
            **{f: None for f in Totals.__dataclass_fields__}
        )
        assert payment.created_by == NO_ACTOR

    @pytest.mark.parametrize(
        ("key", "value", "cls"),
        [
            ("connector", [], Connector),
            ("totals", "x", Totals),
            ("card", [1], PaymentCard),
        ],
    )
    def test_non_object_nested_value_reads_as_empty(self, key, value, cls):
        data = {**V3_EVENT["data"], key: value}
        payment = OttuEvent.from_dict({**V3_EVENT, "data": data}).payment
        assert getattr(payment, key) == cls(
            **{f: None for f in cls.__dataclass_fields__}
        )

    def test_missing_data_keys_read_as_none(self):
        payment = OttuEvent.from_dict({**V3_EVENT, "data": {"status": "paid"}}).payment
        assert (payment.status, payment.session_id, payment.connector.code) == (
            "paid",
            None,
            None,
        )

    def test_unknown_data_key_is_kept_in_data(self):
        raw = {
            **SUBSCRIPTION_CREATED,
            "data": {**SUBSCRIPTION_CREATED["data"], "future_key": 1},
        }
        event = OttuEvent.from_dict(raw)
        assert event.data["future_key"] == 1
        assert event.subscription.subscription_id == "sub_1eQuvS6CkxA8EzDEf6nJ6uLi"
