from django.contrib import admin
from django.urls import path

from .views import WebhookViewReceiveView

urlpatterns = [
    path("admin/", admin.site.urls),
    path(
        "webhook-receiver/",
        WebhookViewReceiveView.as_view(),
        name="webhook-receiver",
    ),
]
