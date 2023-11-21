from django.contrib import admin

from .models import Checkout, Webhook


@admin.register(Checkout)
class CheckoutAdmin(admin.ModelAdmin):
    list_display = (
        "session_id",
        "type",
        "payment_type",
        "amount",
        "currency_code",
        "state",
        "customer_id",
    )
    search_fields = (
        "session_id",
        "type",
        "payment_type",
        "amount",
        "currency_code",
        "state",
        "customer_id",
        "token",
        "agreement",
    )
    list_filter = ["state"]
    ordering = ["-created_at"]


@admin.register(Webhook)
class WebhookAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "session_id",
        "timestamp",
    )
    search_fields = (
        "session_id",
        "payload",
    )
