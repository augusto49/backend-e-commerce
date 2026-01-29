"""
Payment models for the E-commerce Backend.
"""

from django.conf import settings
from django.db import models

from apps.core.models import BaseModel, TimeStampedModel


class Payment(BaseModel):
    """
    Payment model.
    """

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("processing", "Processing"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
        ("refunded", "Refunded"),
        ("cancelled", "Cancelled"),
    ]

    GATEWAY_CHOICES = [
        ("mercadopago", "Mercado Pago"),
        ("pagseguro", "PagSeguro"),
        ("stripe", "Stripe"),
    ]

    METHOD_CHOICES = [
        ("credit_card", "Credit Card"),
        ("debit_card", "Debit Card"),
        ("pix", "PIX"),
        ("boleto", "Boleto"),
    ]

    order = models.ForeignKey(
        "orders.Order",
        on_delete=models.CASCADE,
        related_name="payments",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="payments",
    )

    # Payment info
    gateway = models.CharField(
        "Gateway",
        max_length=20,
        choices=GATEWAY_CHOICES,
    )
    method = models.CharField(
        "Payment Method",
        max_length=20,
        choices=METHOD_CHOICES,
    )
    status = models.CharField(
        "Status",
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
    )

    # Amounts
    amount = models.DecimalField(
        "Amount",
        max_digits=10,
        decimal_places=2,
    )
    fee = models.DecimalField(
        "Gateway Fee",
        max_digits=10,
        decimal_places=2,
        default=0,
    )
    net_amount = models.DecimalField(
        "Net Amount",
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
    )

    # Gateway response
    gateway_payment_id = models.CharField(
        "Gateway Payment ID",
        max_length=255,
        blank=True,
        db_index=True,
    )
    gateway_status = models.CharField(
        "Gateway Status",
        max_length=50,
        blank=True,
    )
    gateway_response = models.JSONField(
        "Gateway Response",
        null=True,
        blank=True,
    )

    # PIX specific
    pix_qr_code = models.TextField("PIX QR Code", blank=True)
    pix_qr_code_base64 = models.TextField("PIX QR Code Base64", blank=True)
    pix_expiration = models.DateTimeField("PIX Expiration", null=True, blank=True)

    # Boleto specific
    boleto_barcode = models.CharField("Boleto Barcode", max_length=100, blank=True)
    boleto_url = models.URLField("Boleto URL", blank=True)
    boleto_expiration = models.DateField("Boleto Expiration", null=True, blank=True)

    # Refund
    refund_reason = models.TextField("Refund Reason", blank=True)
    refunded_at = models.DateTimeField("Refunded At", null=True, blank=True)

    class Meta:
        verbose_name = "Payment"
        verbose_name_plural = "Payments"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Payment {self.id} for Order {self.order.number}"


class PaymentTransaction(TimeStampedModel):
    """
    Track payment transactions/attempts.
    """

    payment = models.ForeignKey(
        Payment,
        on_delete=models.CASCADE,
        related_name="transactions",
    )
    transaction_type = models.CharField(
        "Type",
        max_length=20,
        choices=[
            ("authorization", "Authorization"),
            ("capture", "Capture"),
            ("refund", "Refund"),
            ("chargeback", "Chargeback"),
        ],
    )
    status = models.CharField("Status", max_length=20)
    amount = models.DecimalField(
        "Amount",
        max_digits=10,
        decimal_places=2,
    )
    gateway_transaction_id = models.CharField(
        "Gateway Transaction ID",
        max_length=255,
        blank=True,
    )
    gateway_response = models.JSONField(
        "Gateway Response",
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = "Payment Transaction"
        verbose_name_plural = "Payment Transactions"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.transaction_type} - {self.status}"
