from django.contrib import admin

from .models import Checkout, Webhook


@admin.register(Checkout)
class CheckoutAdmin(admin.ModelAdmin):
    list_display = (
        "session_id",
        "amount",
        "currency_code",
        "state",
        "pg_codes",
        "customer_id",
        "customer_email",
        "customer_phone",
        "customer_first_name",
        "customer_last_name",
        "created_at",
    )
    search_fields = (
        "session_id",
        "amount",
        "currency_code",
        "pg_codes",
        "customer_id",
        "customer_email",
        "customer_phone",
        "customer_first_name",
        "customer_last_name",
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
