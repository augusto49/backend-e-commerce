"""
Cart models for the E-commerce Backend.
Modelos de carrinho para o Backend E-commerce.
"""

from decimal import Decimal

from django.conf import settings
from django.db import models

from apps.core.models import TimeStampedModel


class Cart(TimeStampedModel):
    """
    Shopping cart model.
    Modelo de carrinho de compras.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="carts",
    )
    session_key = models.CharField(
        "Session Key",
        max_length=255,
        null=True,
        blank=True,
        db_index=True,
    )
    coupon = models.ForeignKey(
        "coupons.Coupon",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="carts",
    )

    class Meta:
        verbose_name = "Cart"
        verbose_name_plural = "Carts"

    def __str__(self):
        if self.user:
            return f"Cart for {self.user.email}"
        return f"Cart {self.session_key}"

    @property
    def subtotal(self):
        """
        Calculate cart subtotal.
        Calcula o subtotal do carrinho.
        """
        return sum(item.total_price for item in self.items.all())

    @property
    def discount(self):
        """
        Calculate discount from coupon.
        Calcula desconto do cupom.
        """
        if not self.coupon:
            return Decimal("0.00")

        if not self.coupon.is_valid:
            return Decimal("0.00")

        if self.coupon.discount_type == "percentage":
            discount = self.subtotal * (self.coupon.discount_value / 100)
            if self.coupon.max_discount:
                discount = min(discount, self.coupon.max_discount)
            return discount
        else:
            return min(self.coupon.discount_value, self.subtotal)

    @property
    def total(self):
        """
        Calculate cart total.
        Calcula total do carrinho.
        """
        return max(Decimal("0.00"), self.subtotal - self.discount)

    @property
    def item_count(self):
        """
        Get total number of items in cart.
        Obtém número total de itens no carrinho.
        """
        return sum(item.quantity for item in self.items.all())

    def clear(self):
        """
        Remove all items from cart.
        Remove todos os itens do carrinho.
        """
        self.items.all().delete()
        self.coupon = None
        self.save()


class CartItem(TimeStampedModel):
    """
    Cart item model.
    Modelo de item do carrinho.
    """

    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name="items",
    )
    product = models.ForeignKey(
        "products.Product",
        on_delete=models.CASCADE,
        related_name="cart_items",
    )
    variation = models.ForeignKey(
        "products.ProductVariation",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="cart_items",
    )
    quantity = models.PositiveIntegerField("Quantity", default=1)
    unit_price = models.DecimalField(
        "Unit Price",
        max_digits=10,
        decimal_places=2,
    )

    class Meta:
        verbose_name = "Cart Item"
        verbose_name_plural = "Cart Items"
        unique_together = ["cart", "product", "variation"]

    def __str__(self):
        return f"{self.quantity}x {self.product.name}"

    @property
    def total_price(self):
        """
        Calculate total price for this item.
        Calcula preço total para este item.
        """
        return self.unit_price * self.quantity

    def save(self, *args, **kwargs):
        # Set unit price from product/variation
        # Define preço unitário a partir do produto/variação
        if not self.unit_price:
            if self.variation:
                self.unit_price = self.variation.final_price
            else:
                self.unit_price = self.product.current_price
        super().save(*args, **kwargs)
