"""
Analytics models for the E-commerce Backend.
"""

from django.db import models

from apps.core.models import TimeStampedModel


class PageView(TimeStampedModel):
    """
    Track page views.
    """

    path = models.CharField("Path", max_length=500, db_index=True)
    user_id = models.PositiveIntegerField("User ID", null=True, blank=True)
    session_id = models.CharField("Session ID", max_length=100, db_index=True)
    ip_address = models.GenericIPAddressField("IP Address", null=True, blank=True)
    user_agent = models.CharField("User Agent", max_length=500, blank=True)
    referrer = models.URLField("Referrer", blank=True)

    class Meta:
        verbose_name = "Page View"
        verbose_name_plural = "Page Views"
        indexes = [
            models.Index(fields=["created_at"]),
            models.Index(fields=["path", "created_at"]),
        ]


class ProductView(TimeStampedModel):
    """
    Track product views.
    """

    product = models.ForeignKey(
        "products.Product",
        on_delete=models.CASCADE,
        related_name="analytics_views",
    )
    user_id = models.PositiveIntegerField("User ID", null=True, blank=True)
    session_id = models.CharField("Session ID", max_length=100, db_index=True)

    class Meta:
        verbose_name = "Product View"
        verbose_name_plural = "Product Views"


class SalesSummary(TimeStampedModel):
    """
    Daily sales summary for reporting.
    """

    date = models.DateField("Date", unique=True, db_index=True)
    total_orders = models.PositiveIntegerField("Total Orders", default=0)
    total_revenue = models.DecimalField(
        "Total Revenue",
        max_digits=12,
        decimal_places=2,
        default=0,
    )
    total_items = models.PositiveIntegerField("Total Items", default=0)
    average_order_value = models.DecimalField(
        "Average Order Value",
        max_digits=10,
        decimal_places=2,
        default=0,
    )
    cancelled_orders = models.PositiveIntegerField("Cancelled Orders", default=0)
    refunded_amount = models.DecimalField(
        "Refunded Amount",
        max_digits=12,
        decimal_places=2,
        default=0,
    )

    class Meta:
        verbose_name = "Sales Summary"
        verbose_name_plural = "Sales Summaries"
        ordering = ["-date"]
