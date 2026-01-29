"""
Serializers for the payments app.
"""

from rest_framework import serializers

from .models import Payment, PaymentTransaction


class PaymentSerializer(serializers.ModelSerializer):
    """
    Serializer for payments.
    """

    order_number = serializers.CharField(source="order.number", read_only=True)

    class Meta:
        model = Payment
        fields = [
            "id",
            "order_number",
            "gateway",
            "method",
            "status",
            "amount",
            "pix_qr_code",
            "pix_qr_code_base64",
            "pix_expiration",
            "boleto_barcode",
            "boleto_url",
            "boleto_expiration",
            "created_at",
        ]


class CreatePaymentSerializer(serializers.Serializer):
    """
    Serializer for creating a payment.
    """

    order_id = serializers.IntegerField()
    gateway = serializers.ChoiceField(
        choices=["mercadopago", "pagseguro", "stripe"],
    )
    method = serializers.ChoiceField(
        choices=["credit_card", "debit_card", "pix", "boleto"],
    )

    # Card payment fields
    card_token = serializers.CharField(required=False, allow_blank=True)
    payment_method_id = serializers.CharField(required=False, allow_blank=True)
    installments = serializers.IntegerField(required=False, default=1)


class RefundSerializer(serializers.Serializer):
    """
    Serializer for refund requests.
    """

    amount = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
    )
    reason = serializers.CharField(required=False, allow_blank=True)
