import pytest
from django.shortcuts import reverse

from ottu.contrib.django.models import Webhook
from tests.fake_data import (
    TICKET_26_FIELD_BODY_HEX,
    TICKET_BODY_HEX,
    TICKET_PAYLOAD,
    webhook_payload,
)

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

    def test_documented_18_field_body_signature_accepted(self, client):
        # Positive control for the test below: same payload, documented signature.
        # OTTU_WEBHOOK_KEY in the test settings is the ticket #154780 key.
        payload = {**TICKET_PAYLOAD, "signature": TICKET_BODY_HEX}
        pre_count = Webhook.objects.count()
        response = client.post(
            reverse("webhook-receiver"),
            data=payload,
            content_type="application/json",
        )
        post_count = Webhook.objects.count()
        assert pre_count + 1 == post_count
        assert response.status_code == 200
        assert response.json() == {"detail": "Success"}

    def test_26_field_body_signature_rejected(self, client):
        # The view is body-only. The 26-field recipe is no longer a body fallback:
        # it lives in the Ottu-Signature header (verify_ottu_signature).
        payload = {**TICKET_PAYLOAD, "signature": TICKET_26_FIELD_BODY_HEX}
        pre_count = Webhook.objects.count()
        response = client.post(
            reverse("webhook-receiver"),
            data=payload,
            content_type="application/json",
        )
        post_count = Webhook.objects.count()
        assert pre_count == post_count
        assert response.status_code == 401
        assert response.json() == {"detail": "Unable to verify signature"}

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
