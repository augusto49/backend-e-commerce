"""
URL patterns for the payments app.
"""

from django.urls import path

from .views import (
    CreatePaymentView,
    MercadoPagoWebhookView,
    PaymentDetailView,
    RefundPaymentView,
    StripeWebhookView,
)

urlpatterns = [
    path("", CreatePaymentView.as_view(), name="payment_create"),
    path("<int:payment_id>/", PaymentDetailView.as_view(), name="payment_detail"),
    path("<int:payment_id>/refund/", RefundPaymentView.as_view(), name="payment_refund"),
    # Webhooks
    path("webhooks/mercadopago/", MercadoPagoWebhookView.as_view(), name="webhook_mercadopago"),
    path("webhooks/stripe/", StripeWebhookView.as_view(), name="webhook_stripe"),
]
