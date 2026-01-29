"""
Admin configuration for the payments app.
"""

from django.contrib import admin

from .models import Payment, PaymentTransaction


class PaymentTransactionInline(admin.TabularInline):
    model = PaymentTransaction
    extra = 0
    readonly_fields = [
        "transaction_type",
        "status",
        "amount",
        "gateway_transaction_id",
        "created_at",
    ]


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "order",
        "gateway",
        "method",
        "status",
        "amount",
        "created_at",
    ]
    list_filter = ["status", "gateway", "method", "created_at"]
    search_fields = ["order__number", "user__email", "gateway_payment_id"]
    readonly_fields = [
        "gateway_payment_id",
        "gateway_status",
        "gateway_response",
        "pix_qr_code",
        "pix_qr_code_base64",
        "boleto_barcode",
        "boleto_url",
    ]
    inlines = [PaymentTransactionInline]
