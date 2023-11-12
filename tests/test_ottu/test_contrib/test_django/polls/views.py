from django.conf import settings

from ottu.contrib.django.views import WebhookViewAbstractView


class WebhookViewReceiveView(WebhookViewAbstractView):
    def process_data(self):
        if getattr(settings, "DJ_OTTU_RAISE_WH_ERROR", False):
            raise self.WebHookError("This is test error", status_code=400)
        return super().process_data()
