"""
Admin configuration for the cart app.
"""

from django.contrib import admin

from .models import Cart, CartItem


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ["total_price"]


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "item_count", "subtotal", "total", "updated_at"]
    list_filter = ["updated_at"]
    search_fields = ["user__email", "session_key"]
    readonly_fields = ["subtotal", "discount", "total", "item_count"]
    inlines = [CartItemInline]
