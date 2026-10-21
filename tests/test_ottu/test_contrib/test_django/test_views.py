from types import SimpleNamespace

import pytest
from django.shortcuts import reverse
from django.test import Client, override_settings
from django.urls import path
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from ottu.contrib.django import conf
from ottu.contrib.django.models import Webhook
from ottu.contrib.django.views import WebhookViewAbstractView
from ottu.utils import webhooks
from ottu.utils.webhooks import verify_ottu_signature
from tests.fake_data import (
    TICKET_26_FIELD_BODY_HEX,
    TICKET_BODY_HEX,
    TICKET_HEADER,
    TICKET_PAYLOAD,
    TICKET_T,
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

    def test_lone_surrogate_in_body_returns_401(self, client):
        # json.loads('"\\ud800"') yields a str that cannot be UTF-8 encoded.
        # The view must fail closed (401), not raise (500).
        payload = {
            **TICKET_PAYLOAD,
            "reference_number": TICKET_PAYLOAD["reference_number"] + "\ud800",
            "signature": TICKET_BODY_HEX,
        }
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


# The README Webhooks section's verify() override, exercised as written.
@method_decorator(csrf_exempt, name="dispatch")
class WebhookReceiverView(WebhookViewAbstractView):
    def verify(self) -> bool:
        return verify_ottu_signature(
            payload=self.data,
            header=self.request.headers.get("Ottu-Signature"),
            webhook_key=conf.WEBHOOK_KEY,
        )


urlpatterns = [path("wh-view-header/", WebhookReceiverView.as_view())]


@pytest.mark.urls(__name__)
class TestOttuSignatureHeaderOverride:
    @pytest.fixture(autouse=True)
    def _pin_clock(self, monkeypatch):
        # Replace `time` in the module under test only. The global clock stays real.
        monkeypatch.setattr(webhooks, "time", SimpleNamespace(time=lambda: TICKET_T))

    @pytest.fixture
    def csrf_client(self):
        # Connect posts server-to-server with no CSRF cookie. The middleware is on
        # and enforced, so a missing csrf_exempt shows up as 403 here.
        middleware = ["django.middleware.csrf.CsrfViewMiddleware"]
        with override_settings(MIDDLEWARE=middleware):
            yield Client(enforce_csrf_checks=True)

    @staticmethod
    def _post(client, payload: dict, header: str | None = TICKET_HEADER):
        extra = {} if header is None else {"HTTP_OTTU_SIGNATURE": header}
        return client.post(
            "/wh-view-header/",
            data=payload,
            content_type="application/json",
            **extra,
        )

    def test_genuine_body_and_header_accepted(self, csrf_client):
        pre_count = Webhook.objects.count()
        response = self._post(
            csrf_client, {**TICKET_PAYLOAD, "signature": TICKET_BODY_HEX}
        )
        assert response.status_code == 200
        assert Webhook.objects.count() == pre_count + 1

    def test_missing_header_rejected(self, csrf_client):
        pre_count = Webhook.objects.count()
        response = self._post(
            csrf_client, {**TICKET_PAYLOAD, "signature": TICKET_BODY_HEX}, header=None
        )
        assert response.status_code == 401
        assert Webhook.objects.count() == pre_count

    def test_tampered_token_rejected(self, csrf_client):
        # token.token is covered by v1, not by the body signature.
        tampered = {
            **TICKET_PAYLOAD,
            "token": {**TICKET_PAYLOAD["token"], "token": "attacker-card"},
            "signature": TICKET_BODY_HEX,
        }
        pre_count = Webhook.objects.count()
        response = self._post(csrf_client, tampered)
        assert response.status_code == 401
        assert Webhook.objects.count() == pre_count

    def test_body_signature_is_ignored(self, csrf_client):
        # The override is header-only by design: v1 covers the 18 body fields too.
        response = self._post(csrf_client, {**TICKET_PAYLOAD, "signature": "wrong"})
        assert response.status_code == 200
