"""
Admin configuration for the orders app.
"""

from django.contrib import admin

from .models import Order, OrderItem, OrderStatusHistory


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ["product", "product_name", "product_sku", "unit_price", "total_price"]


class OrderStatusHistoryInline(admin.TabularInline):
    model = OrderStatusHistory
    extra = 0
    readonly_fields = ["status", "notes", "created_by", "created_at"]


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ["number", "user", "status", "total", "created_at"]
    list_filter = ["status", "created_at", "shipping_method"]
    search_fields = ["number", "user__email"]
    readonly_fields = ["number", "subtotal", "discount", "total"]
    inlines = [OrderItemInline, OrderStatusHistoryInline]

    fieldsets = (
        ("Order Info", {
            "fields": ("number", "user", "status")
        }),
        ("Addresses", {
            "fields": ("shipping_address", "billing_address"),
            "classes": ("collapse",),
        }),
        ("Pricing", {
            "fields": ("subtotal", "shipping_cost", "discount", "total", "coupon_code")
        }),
        ("Shipping", {
            "fields": ("shipping_method", "tracking_code", "estimated_delivery")
        }),
        ("Notes", {
            "fields": ("customer_notes", "admin_notes"),
            "classes": ("collapse",),
        }),
    )
