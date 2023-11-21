from django.db import models
from django.utils.translation import gettext_lazy as _

from . import conf


class Checkout(models.Model):
    session_id = models.CharField(_("Session ID"), max_length=100, primary_key=True)
    type = models.CharField(_("Type"), max_length=250)
    payment_type = models.CharField(_("Payment Type"), max_length=250)
    amount = models.CharField(_("Amount"), max_length=20)
    currency_code = models.CharField(_("Currency Code"), max_length=10)
    state = models.CharField(_("State"), max_length=250)
    customer_id = models.CharField(_("Customer ID"), max_length=250, blank=True)
    token = models.CharField(_("Token"), max_length=250, blank=True)
    agreement = models.JSONField(_("Agreement"), blank=True, default=dict)
    extra_params = models.JSONField(_("Extra Params"), blank=True, default=dict)
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
