import copy
import hashlib
import hmac
from types import SimpleNamespace

import pytest

from ottu.utils import webhooks
from ottu.utils.webhooks import (
    _MISSING,
    _SIGNED_FIELDS,
    _V1_SIGNED_FIELDS,
    _resolve_path,
    calculate_hmac_signature,
    verify_ottu_signature,
    verify_signature,
)
from tests.fake_data import (
    TICKET_26_FIELD_BODY_HEX,
    TICKET_BODY_HEX,
    TICKET_HEADER,
    TICKET_KEY,
    TICKET_PAYLOAD,
    TICKET_T,
    TICKET_V1_HEX,
)

KEY = "test-key"

# Ticket #154780 vectors (TICKET_*) are pinned hex literals in tests/fake_data.py.

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

# TICKET_PAYLOAD has a value at these 18 signed paths.
V1_PRESENT_PATHS = [
    "agreement.id",
    "amount",
    "currency_code",
    "customer_email",
    "customer_first_name",
    "extra.autopay.subscription_id",
    "extra.merchant_id",
    "gateway_account",
    "gateway_name",
    "order_no",
    "payment_type",
    "reference_number",
    "result",
    "session_id",
    "state",
    "token.customer_id",
    "token.pg_code",
    "token.token",
]
# ... and none (or "") at these 8.
V1_ABSENT_PATHS = [
    "customer_address_city",
    "customer_address_country",
    "customer_address_line1",
    "customer_address_line2",
    "customer_address_postal_code",
    "customer_address_state",
    "customer_last_name",
    "customer_phone",
]
# The frozen v1 set, spelled out so that any change to it fails a test.
# Any change to this set is a new version (v2), never an edit of v1.
V1_FROZEN_FIELDS = [
    "agreement.id",
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
    "extra.autopay.subscription_id",
    "extra.merchant_id",
    "gateway_account",
    "gateway_name",
    "order_no",
    "payment_type",
    "reference_number",
    "result",
    "session_id",
    "state",
    "token.customer_id",
    "token.pg_code",
    "token.token",
]

# Present in a real webhook payload but deliberately NOT signed by v1.
V1_UNSIGNED_PATHS = [
    ("token.brand", "MC"),
    ("token.number", "**** 9999"),
    ("customer_id", "someone-else"),
    ("signature", "anything"),
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


def _del_path(payload: dict, path: str) -> dict:
    out = copy.deepcopy(payload)
    parts = path.split(".")
    current = out
    for part in parts[:-1]:
        current = current[part]
    del current[parts[-1]]
    return out


def _verify_ticket(payload: dict, header: str | None = TICKET_HEADER) -> bool:
    # The ticket vector is years-stale against the real clock, so most cases
    # switch the age check off. The age check has its own tests.
    return verify_ottu_signature(payload, header, TICKET_KEY, tolerance_seconds=None)


# ---------------------------------------------------------------------------
# Field set tests
# ---------------------------------------------------------------------------


class TestStandardSignedFields:
    def test_exactly_18_fields(self):
        assert len(_SIGNED_FIELDS) == 18

    def test_all_flat_keys(self):
        assert all("." not in f for f in _SIGNED_FIELDS)


class TestV1SignedFields:
    def test_exactly_26_fields(self):
        assert len(_V1_SIGNED_FIELDS) == 26

    def test_list_is_already_sorted(self):
        assert _V1_SIGNED_FIELDS == sorted(_V1_SIGNED_FIELDS)

    def test_contains_all_standard_fields(self):
        assert set(_SIGNED_FIELDS).issubset(set(_V1_SIGNED_FIELDS))

    def test_frozen_set(self):
        # Changing v1 breaks every merchant verifier. Add v2 instead.
        assert list(_V1_SIGNED_FIELDS) == V1_FROZEN_FIELDS

    def test_fixture_paths_cover_the_set(self):
        assert sorted(V1_PRESENT_PATHS + V1_ABSENT_PATHS) == V1_FROZEN_FIELDS


# ---------------------------------------------------------------------------
# _resolve_path (used by the v1 algorithm)
# ---------------------------------------------------------------------------


class TestResolvePath:
    def test_flat(self):
        assert _resolve_path({"amount": "1.000"}, "amount") == "1.000"

    def test_nested(self):
        assert _resolve_path({"token": {"token": "t"}}, "token.token") == "t"

    def test_deep_nested(self):
        payload = {"extra": {"autopay": {"subscription_id": "s"}}}
        assert _resolve_path(payload, "extra.autopay.subscription_id") == "s"

    def test_missing_leaf(self):
        assert _resolve_path({"token": {}}, "token.token") is _MISSING

    def test_missing_namespace(self):
        assert _resolve_path({}, "token.token") is _MISSING

    def test_non_dict_midway(self):
        assert _resolve_path({"token": "not-a-dict"}, "token.token") is _MISSING

    def test_present_null_is_returned_not_missing(self):
        # Resolution returns the real value (None); verify_ottu_signature
        # drops it via the explicit `value is None` guard.
        assert _resolve_path({"token": {"token": None}}, "token.token") is None


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
        assert verify_signature(TICKET_PAYLOAD, TICKET_BODY_HEX, TICKET_KEY) is True

    def test_accepts_docs_3_field_example(self):
        assert (
            verify_signature(DOCS_3_FIELD_PAYLOAD, DOCS_3_FIELD_HEX, TICKET_KEY) is True
        )

    def test_accepts_live_docs_example(self):
        assert verify_signature(DOCS_LIVE_PAYLOAD, DOCS_LIVE_HEX, TICKET_KEY) is True

    def test_rejects_26_field_body_signature(self):
        # F004: a body signature must never cover the extended set by fallback.
        # The signature below is the 26-field recipe over the ticket payload.
        assert (
            verify_signature(TICKET_PAYLOAD, TICKET_26_FIELD_BODY_HEX, TICKET_KEY)
            is False
        )

    def test_rejects_header_v1_hex_as_body_signature(self):
        assert verify_signature(TICKET_PAYLOAD, TICKET_V1_HEX, TICKET_KEY) is False

    def test_rejects_tampered_payload(self):
        tampered = _set_path(TICKET_PAYLOAD, "amount", "999.000")
        assert verify_signature(tampered, TICKET_BODY_HEX, TICKET_KEY) is False

    def test_rejects_wrong_key(self):
        assert verify_signature(TICKET_PAYLOAD, TICKET_BODY_HEX, "wrong-key") is False

    @pytest.mark.parametrize(
        "signature",
        [None, "", "é", TICKET_BODY_HEX.replace("b", "é", 1), 123, b"bb0e1db6"],
        ids=["none", "empty", "non-ascii", "non-ascii-in-hex", "int", "bytes"],
    )
    def test_rejects_bad_signature_without_raising(self, signature):
        # `signature` comes from untrusted JSON. It must return False, never raise.
        assert verify_signature(TICKET_PAYLOAD, signature, TICKET_KEY) is False


# ---------------------------------------------------------------------------
# verify_ottu_signature — Ottu-Signature header, v1
# ---------------------------------------------------------------------------


class TestVerifyOttuSignature:
    def test_ticket_vector_true(self):
        assert _verify_ticket(TICKET_PAYLOAD) is True

    def test_whitespace_around_pairs_is_stripped(self):
        header = f"t={TICKET_T}, v1={TICKET_V1_HEX}"
        assert _verify_ticket(TICKET_PAYLOAD, header) is True
        header = f" t={TICKET_T} ,  v1={TICKET_V1_HEX} "
        assert _verify_ticket(TICKET_PAYLOAD, header) is True

    def test_pair_order_does_not_matter(self):
        header = f"v1={TICKET_V1_HEX},t={TICKET_T}"
        assert _verify_ticket(TICKET_PAYLOAD, header) is True

    @pytest.mark.parametrize("path", V1_PRESENT_PATHS)
    def test_each_signed_value_tampered_false(self, path):
        assert _verify_ticket(_set_path(TICKET_PAYLOAD, path, "X")) is False

    @pytest.mark.parametrize("path", V1_PRESENT_PATHS)
    def test_each_signed_value_removed_false(self, path):
        assert _verify_ticket(_del_path(TICKET_PAYLOAD, path)) is False

    @pytest.mark.parametrize("path", V1_ABSENT_PATHS)
    def test_each_absent_signed_path_added_false(self, path):
        assert _verify_ticket(_set_path(TICKET_PAYLOAD, path, "X")) is False

    def test_t_changed_false(self):
        header = f"t={TICKET_T + 1},v1={TICKET_V1_HEX}"
        assert _verify_ticket(TICKET_PAYLOAD, header) is False

    def test_t_is_signed_exactly_as_received(self):
        # int("01792417440") == TICKET_T, but the signed line is "t=01792417440".
        header = f"t=0{TICKET_T},v1={TICKET_V1_HEX}"
        assert _verify_ticket(TICKET_PAYLOAD, header) is False

    @pytest.mark.parametrize(
        "header",
        [
            None,
            "",
            "   ",
            "garbage",
            f"t={TICKET_T}",
            f"v1={TICKET_V1_HEX}",
            f"t=,v1={TICKET_V1_HEX}",
            f"t={TICKET_T},v1=",
            f"t=abc,v1={TICKET_V1_HEX}",
            f"t=-{TICKET_T},v1={TICKET_V1_HEX}",
            f"t=1.5,v1={TICKET_V1_HEX}",
            f"t=²,v1={TICKET_V1_HEX}",  # str.isdigit() is True, int() raises
            f"t=١٢,v1={TICKET_V1_HEX}",  # Arabic-Indic digits: int() accepts them
            f"t={TICKET_T},v1=é",  # hmac.compare_digest raises on non-ASCII str
            f"t={TICKET_T},v1={TICKET_V1_HEX.upper()}",  # Connect emits lowercase
            f"t={TICKET_T},v2={TICKET_V1_HEX}",
            f"t={TICKET_T},v1={TICKET_V1_HEX[:-1]}",
            f"t={TICKET_T},v1={'0' * 64}",
            ",,,",
            "=,=",
            b"t=1792417440,v1=469f",
            12345,
        ],
        ids=[
            "none",
            "empty",
            "blank",
            "garbage",
            "t-only",
            "v1-only",
            "t-empty",
            "v1-empty",
            "t-alpha",
            "t-negative",
            "t-float",
            "t-superscript-two",
            "t-arabic-digits",
            "v1-non-ascii",
            "v1-uppercase",
            "v2-only",
            "v1-truncated",
            "v1-zeros",
            "commas-only",
            "equals-only",
            "bytes",
            "int",
        ],
    )
    def test_header_missing_or_malformed_false(self, header):
        assert _verify_ticket(TICKET_PAYLOAD, header) is False

    def test_non_dict_payload_false(self):
        # Callers sometimes hold the raw body (str). It must not raise.
        assert _verify_ticket("not-a-dict") is False  # type: ignore[arg-type]
        assert _verify_ticket({}) is False

    def test_non_dict_namespace_false(self):
        assert _verify_ticket(_set_path(TICKET_PAYLOAD, "token", "oops")) is False

    def test_wrong_key_false(self):
        assert (
            verify_ottu_signature(
                TICKET_PAYLOAD, TICKET_HEADER, "wrong-key", tolerance_seconds=None
            )
            is False
        )

    def test_body_signature_hex_as_v1_false(self):
        header = f"t={TICKET_T},v1={TICKET_BODY_HEX}"
        assert _verify_ticket(TICKET_PAYLOAD, header) is False

    def test_26_field_body_signature_hex_as_v1_false(self):
        header = f"t={TICKET_T},v1={TICKET_26_FIELD_BODY_HEX}"
        assert _verify_ticket(TICKET_PAYLOAD, header) is False

    @pytest.mark.parametrize(("path", "value"), V1_UNSIGNED_PATHS)
    def test_unsigned_field_change_keeps_true(self, path, value):
        # AC3: token.brand is not part of v1.
        assert _verify_ticket(_set_path(TICKET_PAYLOAD, path, value)) is True

    def test_unsigned_token_brand_change_true(self):
        changed = _set_path(TICKET_PAYLOAD, "token.brand", "MASTERCARD")
        assert _verify_ticket(changed) is True

    def test_empty_string_equals_absent(self):
        # TICKET_PAYLOAD sends customer_last_name as "". Absent and None match it.
        assert _verify_ticket(_del_path(TICKET_PAYLOAD, "customer_last_name")) is True
        assert (
            _verify_ticket(_set_path(TICKET_PAYLOAD, "customer_last_name", None))
            is True
        )

    @pytest.mark.parametrize("value", ["0", "false", "null", " "])
    def test_falsy_looking_strings_are_signed(self, value):
        # Only absent, None and "" are skipped. The string "0" is a real value.
        changed = _set_path(TICKET_PAYLOAD, "customer_last_name", value)
        assert _verify_ticket(changed) is False

    @pytest.mark.parametrize(
        ("path", "value"),
        [
            ("reference_number", 12345),
            ("reference_number", 0),
            ("reference_number", False),
            ("reference_number", True),
            ("reference_number", 12.5),
            ("reference_number", ["ABC12"]),
            ("reference_number", {"id": "ABC12"}),
            ("token.token", 9923965822244314),
            ("customer_last_name", 0),
            ("customer_last_name", False),
        ],
    )
    def test_non_string_value_false(self, path, value):
        # Languages render non-strings differently (Python True, JavaScript true),
        # so a non-string at a v1 path fails closed instead of being rendered.
        assert _verify_ticket(_set_path(TICKET_PAYLOAD, path, value)) is False

    @pytest.mark.parametrize("value", [12345, ["x"], {"x": 1}])
    def test_non_string_value_at_unsigned_path_ignored(self, value):
        changed = _set_path(TICKET_PAYLOAD, "token.number", value)
        assert _verify_ticket(changed) is True

    @pytest.mark.parametrize(
        "header",
        [
            f"t={TICKET_T},v1={TICKET_V1_HEX},v2=deadbeef",
            f"v2=deadbeef,t={TICKET_T},v1={TICKET_V1_HEX}",
            f"t={TICKET_T},v1={TICKET_V1_HEX},future=1,v3=",
        ],
    )
    def test_unknown_version_ignored(self, header):
        assert _verify_ticket(TICKET_PAYLOAD, header) is True


class TestVerifyOttuSignatureTolerance:
    @staticmethod
    def _set_now(monkeypatch, now: int | float) -> None:
        # Replace `time` in the module under test only. The global clock stays real.
        monkeypatch.setattr(webhooks, "time", SimpleNamespace(time=lambda: now))

    @staticmethod
    def _verify(**kwargs) -> bool:
        return verify_ottu_signature(
            TICKET_PAYLOAD, TICKET_HEADER, TICKET_KEY, **kwargs
        )

    @pytest.mark.parametrize("skew", [0, -1, 1, -299, 299, -300, 300])
    def test_inside_tolerance_true(self, monkeypatch, skew):
        self._set_now(monkeypatch, TICKET_T + skew)
        assert self._verify() is True

    @pytest.mark.parametrize("skew", [-301, 301, -3600, 3600])
    def test_outside_tolerance_false(self, monkeypatch, skew):
        # Past (old t, replay) and future (clock skew) are both rejected.
        self._set_now(monkeypatch, TICKET_T + skew)
        assert self._verify() is False

    def test_fractional_clock_boundary(self, monkeypatch):
        self._set_now(monkeypatch, TICKET_T + 300.4)
        assert self._verify() is False

    def test_default_tolerance_is_300_seconds(self, monkeypatch):
        self._set_now(monkeypatch, TICKET_T + 300)
        assert self._verify() is True
        self._set_now(monkeypatch, TICKET_T + 301)
        assert self._verify() is False

    def test_custom_tolerance(self, monkeypatch):
        self._set_now(monkeypatch, TICKET_T + 60)
        assert self._verify(tolerance_seconds=60) is True
        assert self._verify(tolerance_seconds=59) is False

    def test_none_disables_age_check(self, monkeypatch):
        self._set_now(monkeypatch, TICKET_T + 10**9)
        assert self._verify() is False
        assert self._verify(tolerance_seconds=None) is True

    def test_tolerance_does_not_rescue_bad_signature(self, monkeypatch):
        self._set_now(monkeypatch, TICKET_T)
        changed = _set_path(TICKET_PAYLOAD, "session_id", "attacker")
        assert verify_ottu_signature(changed, TICKET_HEADER, TICKET_KEY) is False
