import json
import logging

from django.http import JsonResponse
from django.views.generic.base import ContextMixin, View

from ...errors import WebhookProcessingError
from ...utils import verify_signature
from . import conf
from .models import Webhook

logger = logging.getLogger("ottu-py")


class WebhookViewAbstractView(ContextMixin, View):
    WebHookError = WebhookProcessingError
    WebHookModel = Webhook
    status_codes = {
        "success": 200,
        "failure": 400,
        "unverified": 401,
    }
    _data = None

    @property
    def data(self):
        if self._data is None:
            self._data = self.request.POST or json.loads(
                self.request.body.decode("utf-8"),
            )
        return self._data

    def verify(self) -> bool:
        signature_server = self.data.get("signature", "")
        return verify_signature(
            payload=self.data,
            signature=signature_server,
            webhook_key=conf.WEBHOOK_KEY,
        )

    def clean_data(self, processed_data):
        # Use either `processed_data` or `self.data` to create a dict
        return self.data

    def process_data(self):
        # Do something with `self.data`
        return self.data

    def save_data(self, processed_data):
        cleaned_data = self.clean_data(processed_data)
        instance = self.WebHookModel.create_from_webhook(data=cleaned_data)
        return instance

    def post(self, request, *args, **kwargs):
        logger.info(f"Webhook received: {self.data}")
        verified = self.verify()
        if not verified:
            return JsonResponse(
                data={"detail": "Unable to verify signature"},
                status=self.status_codes["unverified"],
            )
        try:
            processed_data = self.process_data()
            self.save_data(processed_data=processed_data)
            return JsonResponse(
                data={"detail": "Success"},
                status=self.status_codes["success"],
            )
        except self.WebHookError:
            return JsonResponse(
                data={"detail": "Failed to process webhook"},
                status=self.status_codes["failure"],
            )
