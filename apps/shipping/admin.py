"""
Admin configuration for the shipping app.
"""

from django.contrib import admin

from .models import ShippingMethod, ShippingRate


class ShippingRateInline(admin.TabularInline):
    model = ShippingRate
    extra = 0


@admin.register(ShippingMethod)
class ShippingMethodAdmin(admin.ModelAdmin):
    list_display = ["name", "code", "carrier", "base_price", "is_active"]
    list_filter = ["carrier", "is_active"]
    search_fields = ["name", "code"]
    inlines = [ShippingRateInline]
