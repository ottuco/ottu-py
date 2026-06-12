import pytest
from django.shortcuts import reverse

from ottu.contrib.django.models import Webhook
from ottu.utils.webhooks import calculate_subscription_hmac_signature
from tests.fake_data import webhook_payload

pytestmark = pytest.mark.django_db


class TestWebhookReceiveView:
    def test_success(self, client):
        pre_count = Webhook.objects.count()
        response = client.post(
            reverse("webhook-receiver"),
            data=webhook_payload,
            content_type="application/json",
        )
        post_count = Webhook.objects.count()
        assert pre_count + 1 == post_count
        assert response.status_code == 200
        assert response.json() == {"detail": "Success"}

    def test_unverified(self, client):
        pre_count = Webhook.objects.count()
        payload = {**webhook_payload, "signature": "invalid-signature"}
        response = client.post(
            reverse("webhook-receiver"),
            data=payload,
            content_type="application/json",
        )
        post_count = Webhook.objects.count()
        assert pre_count == post_count
        assert response.status_code == 401
        assert response.json() == {"detail": "Unable to verify signature"}

    def test_processing_error(self, client, custom_wh_error):
        pre_count = Webhook.objects.count()
        response = client.post(
            reverse("webhook-receiver"),
            data=webhook_payload,
            content_type="application/json",
        )
        post_count = Webhook.objects.count()
        assert pre_count == post_count
        assert response.status_code == 400
        assert response.json() == {"detail": "Failed to process webhook"}

    def test_subscription_signature_accepted(self, client):
        # Subscription-algorithm webhooks (betabulk / feat153560+) must pass via the fallback.
        _webhook_key = "pu9MpX3yPR"
        payload = {
            "amount": "10.000",
            "payment_type": "auto_debit",
            "result": "success",
            "session_id": "sess-sub-1",
            "state": "paid",
            "token": {"token": "tok-sub-1", "pg_code": "knet", "customer_id": "cust-sub-1"},
        }
        payload["signature"] = calculate_subscription_hmac_signature(payload, _webhook_key)
        pre_count = Webhook.objects.count()
        response = client.post(
            reverse("webhook-receiver"),
            data=payload,
            content_type="application/json",
        )
        post_count = Webhook.objects.count()
        assert pre_count + 1 == post_count
        assert response.status_code == 200

    def test_null_signature_returns_401(self, client):
        # JSON null signature must return 401, not crash with 500.
        payload = {**webhook_payload, "signature": None}
        pre_count = Webhook.objects.count()
        response = client.post(
            reverse("webhook-receiver"),
            data=payload,
            content_type="application/json",
        )
        post_count = Webhook.objects.count()
        assert pre_count == post_count
        assert response.status_code == 401
