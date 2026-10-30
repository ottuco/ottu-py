import copy
import hashlib
import hmac
import json
from types import SimpleNamespace

import pytest

from ottu.utils import webhooks
from ottu.utils.webhooks import (
    _SIGNED_FIELDS,
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
