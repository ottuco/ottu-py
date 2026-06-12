import copy
import hashlib
import hmac

import pytest

from ottu.utils.webhooks import (
    _MISSING,
    _SIGNED_FIELDS,
    _SUBSCRIPTION_SIGNED_FIELDS,
    _resolve_path,
    calculate_hmac_signature,
    calculate_subscription_hmac_signature,
    verify_signature,
)

KEY = "test-key"

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
# Canonical form: sorted(_SIGNED_FIELDS) keys present in payload, key+value, no delimiter.
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

# ---------------------------------------------------------------------------
# Subscription (26-field) test fixtures
# ---------------------------------------------------------------------------

# Golden payload + byte-pinned canonical form — the cross-repo contract test from
# ticket #154780 / Connect journal 899230. Skip-if-empty: only present, truthy
# fields appear; `token.brand` is unsigned, empty `state` and every absent field
# are dropped. Joined with "\n", no trailing newline.
GOLDEN_PAYLOAD = {
    "amount": "100.000",
    "result": "success",
    "session_id": "sess-1",
    "token": {"token": "tok-1", "brand": "VISA"},
    "state": "",
}
GOLDEN_MESSAGE = "\n".join(
    [
        "amount=100.000",
        "result=success",
        "session_id=sess-1",
        "token.token=tok-1",
    ]
)
GOLDEN_DIGEST_LITERAL = (
    "46ba93a62680c8750567583bb8074e37ccaadc6f374268b78a0c574c8424baff"
)

# A real betabulk auto-pay webhook (Connect feat/153560). The live signature was
# verified byte-for-byte against the production signer on 2026-06-04 with the
# merchant HMAC key (not committed). Here we pin the canonical skip-message this
# exact shape produces: `agreement` absent -> dropped, `extra.merchant_id` present,
# `extra.autopay.subscription_id` absent -> dropped, top-level `customer_id` and
# `token.brand`/`token.number`/`token.agreements` unsigned.
BETABULK_PAYLOAD = {
    "amount": "10.000",
    "currency_code": "KWD",
    "customer_email": "ankit.e2e@example.com",
    "customer_first_name": "Ankit",
    "customer_id": "cust_e2e_3",
    "customer_last_name": "E2E",
    "customer_phone": "+96550000000",
    "extra": {"merchant_id": "betabulk.ottu.net"},
    "gateway_account": "autopay",
    "gateway_name": "mpgs",
    "order_no": "AP-E2E-3",
    "payment_type": "one_off",
    "reference_number": "betabuG3WYV",
    "result": "success",
    "session_id": "42c936ef34f19f14a58115d5e49a9a56dc19a48e",
    "state": "paid",
    "token": {
        "brand": "MASTERCARD",
        "token": "9094504640665278",
        "number": "**** 0008",
        "pg_code": "autopay",
        "agreements": [],
        "customer_id": "cust_e2e_3",
    },
}
BETABULK_MESSAGE = "\n".join(
    [
        "amount=10.000",
        "currency_code=KWD",
        "customer_email=ankit.e2e@example.com",
        "customer_first_name=Ankit",
        "customer_last_name=E2E",
        "customer_phone=+96550000000",
        "extra.merchant_id=betabulk.ottu.net",
        "gateway_account=autopay",
        "gateway_name=mpgs",
        "order_no=AP-E2E-3",
        "payment_type=one_off",
        "reference_number=betabuG3WYV",
        "result=success",
        "session_id=42c936ef34f19f14a58115d5e49a9a56dc19a48e",
        "state=paid",
        "token.customer_id=cust_e2e_3",
        "token.pg_code=autopay",
        "token.token=9094504640665278",
    ]
)

# The 8 subscription-specific fields added on top of the standard 18.
SUBSCRIPTION_ONLY_PATHS = [
    "agreement.id",
    "extra.autopay.subscription_id",
    "extra.merchant_id",
    "payment_type",
    "session_id",
    "token.customer_id",
    "token.pg_code",
    "token.token",
]

# Present in a real webhook payload but deliberately NOT signed by either algorithm.
UNSIGNED_PATHS = [
    ("token.brand", "MASTERCARD"),
    ("token.number", "**** 9999"),
    ("customer_id", "someone-else"),
    ("amount_details.total", "999.000"),
]


def _digest(message: str) -> str:
    return hmac.new(
        KEY.encode("utf8"), message.encode("utf8"), hashlib.sha256
    ).hexdigest()


def _full_subscription_payload() -> dict:
    """Full payload with all subscription fields present."""
    return {
        "agreement": {"id": "agr-1"},
        "amount": "100.000",
        "currency_code": "KWD",
        "customer_email": "a@b.com",
        "customer_first_name": "Ankit",
        "customer_last_name": "Test",
        "customer_phone": "+96550000000",
        "order_no": "ord-1",
        "payment_type": "auto_debit",
        "reference_number": "ref-1",
        "result": "success",
        "session_id": "sess-1",
        "state": "paid",
        "customer_id": "cust-top",
        "extra": {"merchant_id": "m-1", "autopay": {"subscription_id": "sub-1"}},
        "token": {
            "token": "tok-1",
            "pg_code": "knet",
            "customer_id": "cust-1",
            "brand": "VISA",
            "number": "**** 1111",
        },
    }


def _set_path(payload: dict, path: str, value: object) -> dict:
    out = copy.deepcopy(payload)
    parts = path.split(".")
    current = out
    for part in parts[:-1]:
        current = current.setdefault(part, {})
    current[parts[-1]] = value
    return out


# ---------------------------------------------------------------------------
# Field set tests
# ---------------------------------------------------------------------------

class TestStandardSignedFields:
    def test_exactly_18_fields(self):
        assert len(_SIGNED_FIELDS) == 18

    def test_all_flat_keys(self):
        assert all("." not in f for f in _SIGNED_FIELDS)


class TestSubscriptionSignedFields:
    def test_exactly_26_fields(self):
        assert len(_SUBSCRIPTION_SIGNED_FIELDS) == 26

    def test_list_is_already_sorted(self):
        assert _SUBSCRIPTION_SIGNED_FIELDS == sorted(_SUBSCRIPTION_SIGNED_FIELDS)

    def test_contains_all_standard_fields(self):
        # Every standard field must also appear in the subscription set.
        assert set(_SIGNED_FIELDS).issubset(set(_SUBSCRIPTION_SIGNED_FIELDS))


# ---------------------------------------------------------------------------
# _resolve_path (used by subscription algorithm only)
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
        # Resolution returns the real value (None); calculate_subscription_hmac_signature
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
        extra = {**_STD_PAYLOAD, "customer_id": "someone-else", "session_id": "hijacked"}
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
# Subscription 26-field algorithm
# ---------------------------------------------------------------------------

class TestSubscriptionGoldenVector:
    def test_message_digest_matches_literal(self):
        assert _digest(GOLDEN_MESSAGE) == GOLDEN_DIGEST_LITERAL

    def test_calculate_reproduces_golden(self):
        assert calculate_subscription_hmac_signature(GOLDEN_PAYLOAD, KEY) == GOLDEN_DIGEST_LITERAL

    def test_real_betabulk_payload_canonicalization(self):
        # Pins the exact skip-message a live Connect feat/153560 auto-pay webhook
        # produces (signature verified against production with the real key).
        assert calculate_subscription_hmac_signature(BETABULK_PAYLOAD, KEY) == _digest(
            BETABULK_MESSAGE
        )


class TestSubscriptionSkipBehavior:
    def test_missing_fields_skipped(self):
        assert calculate_subscription_hmac_signature({}, KEY) == _digest("")

    def test_empty_string_skipped_like_missing(self):
        with_empty = calculate_subscription_hmac_signature({"amount": "1.000", "state": ""}, KEY)
        without = calculate_subscription_hmac_signature({"amount": "1.000"}, KEY)
        assert with_empty == without

    def test_zero_string_not_skipped(self):
        # "0" is a valid non-empty string — must be included, not treated as absent.
        with_zero = calculate_subscription_hmac_signature({"amount": "0"}, KEY)
        without_amount = calculate_subscription_hmac_signature({}, KEY)
        assert with_zero != without_amount

    def test_unsigned_nested_keys_excluded(self):
        # token.brand is present but unsigned; it must not enter the message.
        assert calculate_subscription_hmac_signature(
            {"token": {"token": "x", "brand": "VISA"}}, KEY
        ) == _digest("token.token=x")


class TestSubscriptionTamperFields:
    @pytest.mark.parametrize("path", SUBSCRIPTION_ONLY_PATHS)
    def test_tampering_breaks_signature(self, path):
        base = _full_subscription_payload()
        original = calculate_subscription_hmac_signature(base, KEY)
        tampered = _set_path(base, path, "HACKED")
        assert calculate_subscription_hmac_signature(tampered, KEY) != original

    @pytest.mark.parametrize("path", SUBSCRIPTION_ONLY_PATHS)
    def test_emptying_breaks_signature(self, path):
        base = _full_subscription_payload()
        original = calculate_subscription_hmac_signature(base, KEY)
        emptied = _set_path(base, path, "")
        assert calculate_subscription_hmac_signature(emptied, KEY) != original

    @pytest.mark.parametrize("path", SUBSCRIPTION_ONLY_PATHS)
    def test_nulling_breaks_signature(self, path):
        # None is treated as absent — removes the field from the message, breaking the signature.
        base = _full_subscription_payload()
        original = calculate_subscription_hmac_signature(base, KEY)
        nulled = _set_path(base, path, None)
        assert calculate_subscription_hmac_signature(nulled, KEY) != original


class TestSubscriptionUnsignedFields:
    @pytest.mark.parametrize("path,value", UNSIGNED_PATHS)
    def test_changing_unsigned_field_keeps_signature(self, path, value):
        base = _full_subscription_payload()
        original = calculate_subscription_hmac_signature(base, KEY)
        changed = _set_path(base, path, value)
        assert calculate_subscription_hmac_signature(changed, KEY) == original


class TestSubscriptionMissingAndNull:
    def test_missing_namespace_does_not_raise(self):
        sig = calculate_subscription_hmac_signature({"amount": "1.000"}, KEY)
        assert isinstance(sig, str) and len(sig) == 64

    def test_present_null_skipped_like_missing(self):
        with_null = calculate_subscription_hmac_signature({"token": {"token": None}}, KEY)
        without = calculate_subscription_hmac_signature({}, KEY)
        assert with_null == without


# ---------------------------------------------------------------------------
# verify_signature — dual-scheme
# ---------------------------------------------------------------------------

class TestVerifySignature:
    def test_accepts_standard_signature(self):
        sig = calculate_hmac_signature(_STD_PAYLOAD, KEY)
        assert verify_signature(_STD_PAYLOAD, sig, KEY) is True

    def test_accepts_subscription_signature(self):
        # betabulk / feat153560+ instances use the subscription algorithm.
        payload = _full_subscription_payload()
        sig = calculate_subscription_hmac_signature(payload, KEY)
        assert verify_signature(payload, sig, KEY) is True

    def test_rejects_tampered_standard_payload(self):
        sig = calculate_hmac_signature(_STD_PAYLOAD, KEY)
        tampered = {**_STD_PAYLOAD, "amount": "999.000"}
        assert verify_signature(tampered, sig, KEY) is False

    def test_rejects_tampered_subscription_payload(self):
        payload = _full_subscription_payload()
        sig = calculate_subscription_hmac_signature(payload, KEY)
        tampered = _set_path(payload, "token.token", "evil-token")
        assert verify_signature(tampered, sig, KEY) is False

    def test_rejects_wrong_key(self):
        sig = calculate_hmac_signature(_STD_PAYLOAD, KEY)
        assert verify_signature(_STD_PAYLOAD, sig, "wrong-key") is False

    def test_two_algorithms_produce_distinct_signatures(self):
        # The two algorithms must never accidentally produce the same digest for the
        # same payload — that would allow a subscription signature to pass as standard.
        payload = _full_subscription_payload()
        assert calculate_hmac_signature(payload, KEY) != calculate_subscription_hmac_signature(payload, KEY)
