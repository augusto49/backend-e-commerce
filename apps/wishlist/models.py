"""
Wishlist models for the E-commerce Backend.
"""

from django.conf import settings
from django.db import models

from apps.core.models import TimeStampedModel


class WishlistItem(TimeStampedModel):
    """
    Wishlist item model.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="wishlist_items",
    )
    product = models.ForeignKey(
        "products.Product",
        on_delete=models.CASCADE,
        related_name="wishlist_items",
    )

    class Meta:
        verbose_name = "Wishlist Item"
        verbose_name_plural = "Wishlist Items"
        unique_together = ["user", "product"]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.email} - {self.product.name}"
