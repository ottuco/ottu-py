import pytest
from django.shortcuts import reverse

from ottu.contrib.django.models import Webhook
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
