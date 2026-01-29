"""
Order models for the E-commerce Backend.
"""

from decimal import Decimal

from django.conf import settings
from django.db import models

from apps.core.models import BaseModel, TimeStampedModel
from apps.core.utils import generate_order_number


class Order(BaseModel):
    """
    Order model.
    """

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("awaiting_payment", "Awaiting Payment"),
        ("paid", "Paid"),
        ("processing", "Processing"),
        ("shipped", "Shipped"),
        ("delivered", "Delivered"),
        ("cancelled", "Cancelled"),
        ("refunded", "Refunded"),
    ]

    # Order identification
    number = models.CharField(
        "Order Number",
        max_length=20,
        unique=True,
        db_index=True,
    )

    # User
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="orders",
    )

    # Status
    status = models.CharField(
        "Status",
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
        db_index=True,
    )

    # Addresses (stored as JSON for historical record)
    shipping_address = models.JSONField("Shipping Address")
    billing_address = models.JSONField("Billing Address", null=True, blank=True)

    # Pricing
    subtotal = models.DecimalField(
        "Subtotal",
        max_digits=10,
        decimal_places=2,
    )
    shipping_cost = models.DecimalField(
        "Shipping Cost",
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
    )
    discount = models.DecimalField(
        "Discount",
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
    )
    total = models.DecimalField(
        "Total",
        max_digits=10,
        decimal_places=2,
    )

    # Coupon
    coupon = models.ForeignKey(
        "coupons.Coupon",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="orders",
    )
    coupon_code = models.CharField(
        "Coupon Code",
        max_length=50,
        blank=True,
    )

    # Shipping
    shipping_method = models.CharField(
        "Shipping Method",
        max_length=100,
        blank=True,
    )
    tracking_code = models.CharField(
        "Tracking Code",
        max_length=100,
        blank=True,
    )
    estimated_delivery = models.DateField(
        "Estimated Delivery",
        null=True,
        blank=True,
    )

    # Notes
    customer_notes = models.TextField("Customer Notes", blank=True)
    admin_notes = models.TextField("Admin Notes", blank=True)

    class Meta:
        verbose_name = "Order"
        verbose_name_plural = "Orders"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["number"]),
            models.Index(fields=["user", "status"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return f"Order {self.number}"

    def save(self, *args, **kwargs):
        if not self.number:
            self.number = generate_order_number()
        super().save(*args, **kwargs)

    @property
    def can_cancel(self):
        """Check if order can be cancelled."""
        return self.status in ["pending", "awaiting_payment", "paid"]


class OrderItem(TimeStampedModel):
    """
    Order item model.
    """

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items",
    )
    product = models.ForeignKey(
        "products.Product",
        on_delete=models.SET_NULL,
        null=True,
        related_name="order_items",
    )
    variation = models.ForeignKey(
        "products.ProductVariation",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="order_items",
    )

    # Snapshot of product info at time of order
    product_name = models.CharField("Product Name", max_length=255)
    product_sku = models.CharField("Product SKU", max_length=50)
    variation_name = models.CharField("Variation Name", max_length=100, blank=True)

    quantity = models.PositiveIntegerField("Quantity", default=1)
    unit_price = models.DecimalField(
        "Unit Price",
        max_digits=10,
        decimal_places=2,
    )
    total_price = models.DecimalField(
        "Total Price",
        max_digits=10,
        decimal_places=2,
    )

    class Meta:
        verbose_name = "Order Item"
        verbose_name_plural = "Order Items"

    def __str__(self):
        return f"{self.quantity}x {self.product_name}"

    def save(self, *args, **kwargs):
        self.total_price = self.unit_price * self.quantity
        super().save(*args, **kwargs)


class OrderStatusHistory(TimeStampedModel):
    """
    Track order status changes.
    """

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="status_history",
    )
    status = models.CharField("Status", max_length=20)
    notes = models.TextField("Notes", blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = "Order Status History"
        verbose_name_plural = "Order Status Histories"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.order.number} - {self.status}"
