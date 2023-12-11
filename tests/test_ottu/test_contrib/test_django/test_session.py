import json

import pytest

pytestmark = pytest.mark.django_db


class TestSession:
    def test_webhook_url_from_conf(
        self,
        httpx_mock,
        response_checkout,
        payload_minimal_checkout,
        ottu,
    ):
        httpx_mock.add_response(
            url="https://test.ottu.dev/b/checkout/v1/pymt-txn/",
            method="POST",
            status_code=200,
            json={"detail": "Anything"},
        )

        # Make sure the `ottu.session` is not set
        assert ottu.session.session_id is None

        # Make the request
        ottu.checkout(**payload_minimal_checkout)

        request = httpx_mock.get_request()
        content = json.loads(request.content.decode())
        webhook_url_auto = content["webhook_url"]
        assert webhook_url_auto == "https://test.client.dev/webhook-receiver/"

    def test_webhook_url_explicit(
        self,
        httpx_mock,
        response_checkout,
        payload_minimal_checkout,
        ottu,
    ):
        httpx_mock.add_response(
            url="https://test.ottu.dev/b/checkout/v1/pymt-txn/",
            method="POST",
            status_code=200,
            json={"detail": "Anything"},
        )

        # Make sure the `ottu.session` is not set
        assert ottu.session.session_id is None

        # Make the request
        ottu.checkout(
            **{
                **payload_minimal_checkout,
                "webhook_url": "https://test.client.dev/webhook-receiver-1234/",
            },
        )

        request = httpx_mock.get_request()
        content = json.loads(request.content.decode())
        webhook_url_auto = content["webhook_url"]
        assert webhook_url_auto == "https://test.client.dev/webhook-receiver-1234/"
