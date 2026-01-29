"""
Admin configuration for the coupons app.
"""

from django.contrib import admin

from .models import Coupon, CouponUsage


class CouponUsageInline(admin.TabularInline):
    model = CouponUsage
    extra = 0
    readonly_fields = ["user", "order", "created_at"]


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = [
        "code",
        "discount_type",
        "discount_value",
        "is_active",
        "times_used",
        "usage_limit",
        "valid_until",
    ]
    list_filter = ["is_active", "discount_type", "valid_from", "valid_until"]
    search_fields = ["code", "description"]
    filter_horizontal = ["specific_products", "specific_categories"]
    readonly_fields = ["times_used"]
    inlines = [CouponUsageInline]
