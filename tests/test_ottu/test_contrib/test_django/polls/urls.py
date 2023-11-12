from django.urls import path

from .views import WebhookViewReceiveView

urlpatterns = [
    path(
        "webhook-receiver/",
        WebhookViewReceiveView.as_view(),
        name="webhook-receiver",
    ),
]
