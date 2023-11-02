import json
from typing import Any

from django.db import models
from django.utils.translation import gettext_lazy as _

from ..session import PaymentMethod
from . import conf


class PaymentMethodEncoder(json.JSONEncoder):
    def default(self, o: Any) -> Any:
        if isinstance(o, PaymentMethod):
            return o.__dict__
        return json.JSONEncoder.default(self, o)


class Checkout(models.Model):
    session_id = models.CharField(_("Session ID"), max_length=100, primary_key=True)
    amount = models.CharField(_("Amount"), max_length=20)
    attachment = models.URLField(_("Attachment"), max_length=250, blank=True)
    attachment_short_url = models.URLField(
        _("Attachment Short URL"),
        max_length=250,
        blank=True,
    )
    billing_address = models.CharField(_("Billing Address"), max_length=250, blank=True)
    checkout_short_url = models.URLField(
        _("Checkout Short URL"),
        max_length=250,
        blank=True,
    )
    checkout_url = models.URLField(_("Checkout URL"), max_length=250, blank=True)
    currency_code = models.CharField(_("Currency Code"), max_length=10, blank=True)
    customer_email = models.EmailField(_("Customer Email"), max_length=250, blank=True)
    customer_first_name = models.CharField(
        _("Customer First Name"),
        max_length=250,
        blank=True,
    )
    customer_last_name = models.CharField(
        _("Customer Last Name"),
        max_length=250,
        blank=True,
    )
    customer_id = models.CharField(_("Customer ID"), max_length=250, blank=True)
    customer_phone = models.CharField(_("Customer Phone"), max_length=250, blank=True)
    due_datetime = models.CharField(_("Due Datetime"), max_length=100, blank=True)
    email_recipients = models.CharField(
        _("Email Recipients"),
        max_length=250,
        blank=True,
    )
    expiration_time = models.CharField(_("Expiration Time"), max_length=100, blank=True)
    extra = models.JSONField(_("Extra"), blank=True, default=dict)
    initiator_id = models.CharField(_("Initiator ID"), max_length=250, blank=True)
    language = models.CharField(_("Language"), max_length=10, blank=True)
    mode = models.CharField(_("Mode"), max_length=250, blank=True)
    notifications = models.CharField(_("Notifications"), max_length=250, blank=True)
    operation = models.CharField(_("Operation"), max_length=250, blank=True)
    order_no = models.CharField(_("Order No"), max_length=250, blank=True)
    payment_methods = models.JSONField(
        _("Payment Methods"),
        blank=True,
        default=dict,
        encoder=PaymentMethodEncoder,
    )
    pg_codes = models.JSONField(_("PG Codes"), blank=True, default=dict)
    qr_code_url = models.URLField(_("QR Code URL"), max_length=250, blank=True)
    redirect_url = models.URLField(_("Redirect URL"), max_length=250, blank=True)
    shipping_address = models.CharField(
        _("Shipping Address"),
        max_length=250,
        blank=True,
    )
    state = models.CharField(_("State"), max_length=250, blank=True)
    type = models.CharField(_("Type"), max_length=250, blank=True)
    vendor_name = models.CharField(_("Vendor Name"), max_length=250, blank=True)
    webhook_url = models.URLField(_("Webhook URL"), max_length=250, blank=True)

    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated At"), auto_now=True)

    class Meta:
        verbose_name = _("Checkout")
        verbose_name_plural = _("Checkout")
        abstract = conf.ABSTRACT_CHECKOUT_MODEL

    def __str__(self):
        return str(self.session_id)


class Webhook(models.Model):
    session_id = models.CharField(_("Session ID"), max_length=250)
    checkout = models.ForeignKey(
        Checkout,
        verbose_name=_(
            "Checkout",
        ),
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    payload = models.JSONField(_("Payload"), blank=True, default=dict)
    timestamp = models.DateTimeField(_("Timestamp"), auto_now_add=True)

    class Meta:
        verbose_name = _("Webhook")
        verbose_name_plural = _("Webhooks")
        abstract = conf.ABSTRACT_WEBHOOK_MODEL

    def __str__(self):
        return str(self.session_id)

    def update_instance_from_webhook(self, data: dict):
        for field, value in data.items():
            setattr(self, field, value)
        self.save()

    @classmethod
    def create_from_webhook(cls, data):
        session_id = data.get("session_id", "")

        checkout = None
        if session_id:
            checkout = Checkout.objects.filter(session_id=session_id).first()

        instance = cls.objects.create(
            session_id=session_id,
            checkout=checkout,
            payload=data,
        )

        if checkout:
            for field, value in data.items():
                setattr(checkout, field, value)
            checkout.save()
        return instance
