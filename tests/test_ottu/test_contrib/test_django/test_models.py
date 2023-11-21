import json

import pytest

from ottu.contrib.django.models import Checkout, Webhook
from ottu.json import PaymentMethodEncoder
from ottu.session import PaymentMethod

pytestmark = pytest.mark.django_db


class TestWebhookNModel:
    def test_create_from_webhook(self, response_checkout):
        session_id = response_checkout["session_id"]
        assert Webhook.objects.filter(session_id=session_id).first() is None
        assert Checkout.objects.filter(session_id=session_id).first() is None

        webhook = Webhook.create_from_webhook(response_checkout)
        assert webhook.session_id == response_checkout["session_id"]
        assert webhook.checkout is None  # because we didn't create checkout

    def test_create_from_webhook_with_existing_checkout(self, response_checkout):
        session_id = response_checkout["session_id"]
        checkout = Checkout.objects.create(session_id=session_id)

        webhook = Webhook.create_from_webhook(response_checkout)

        assert webhook.session_id == session_id
        assert webhook.checkout == checkout
        assert webhook.checkout.state == response_checkout["state"]


class TestPaymentMethodEncoder:
    def test_success(self):
        expected_dict = {
            "code": "foo-abcd",
            "name": "Amex Card",
            "pg": None,
            "type": None,
            "amount": None,
            "currency_code": None,
            "fee": None,
            "fee_description": None,
            "icon": None,
            "flow": None,
            "redirect_url": None,
        }
        pm = PaymentMethod(code="foo-abcd", name="Amex Card")
        result = json.dumps(pm, cls=PaymentMethodEncoder)
        assert result == json.dumps(expected_dict)

    def test_fail(self):
        class Foo:
            pass

        foo = Foo()
        with pytest.raises(TypeError):
            json.dumps(foo, cls=PaymentMethodEncoder)
