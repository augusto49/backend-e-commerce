"""
Admin configuration for the analytics app.
"""

from django.contrib import admin

from .models import PageView, ProductView, SalesSummary


@admin.register(SalesSummary)
class SalesSummaryAdmin(admin.ModelAdmin):
    list_display = [
        "date",
        "total_orders",
        "total_revenue",
        "average_order_value",
        "cancelled_orders",
    ]
    list_filter = ["date"]
    ordering = ["-date"]


@admin.register(PageView)
class PageViewAdmin(admin.ModelAdmin):
    list_display = ["path", "user_id", "session_id", "created_at"]
    list_filter = ["created_at"]
    search_fields = ["path"]


@admin.register(ProductView)
class ProductViewAdmin(admin.ModelAdmin):
    list_display = ["product", "user_id", "session_id", "created_at"]
    list_filter = ["created_at"]
