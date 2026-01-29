"""
Coupon models for the E-commerce Backend.
Modelos de cupom para o Backend E-commerce.
"""

from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils import timezone

from apps.core.models import BaseModel


class Coupon(BaseModel):
    """
    Discount coupon model.
    Modelo de cupom de desconto.
    """

    DISCOUNT_TYPE_CHOICES = [
        ("percentage", "Percentage"),
        ("fixed", "Fixed Amount"),
    ]

    code = models.CharField("Code", max_length=50, unique=True, db_index=True)
    description = models.TextField("Description", blank=True)

    discount_type = models.CharField(
        "Discount Type",
        max_length=20,
        choices=DISCOUNT_TYPE_CHOICES,
        default="percentage",
    )
    discount_value = models.DecimalField(
        "Discount Value",
        max_digits=10,
        decimal_places=2,
        help_text="Percentage (0-100) or fixed amount",
    )
    max_discount = models.DecimalField(
        "Maximum Discount",
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Maximum discount for percentage coupons",
    )

    min_order_value = models.DecimalField(
        "Minimum Order Value",
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    # Usage limits
    # Limites de uso
    usage_limit = models.PositiveIntegerField(
        "Usage Limit",
        null=True,
        blank=True,
        help_text="Total times this coupon can be used",
    )
    usage_limit_per_user = models.PositiveIntegerField(
        "Usage Limit per User",
        default=1,
    )
    times_used = models.PositiveIntegerField("Times Used", default=0)

    # Validity
    # Validade
    is_active = models.BooleanField("Active", default=True)
    valid_from = models.DateTimeField("Valid From", default=timezone.now)
    valid_until = models.DateTimeField("Valid Until", null=True, blank=True)

    # Restrictions
    # Restrições
    first_purchase_only = models.BooleanField(
        "First Purchase Only",
        default=False,
    )
    specific_products = models.ManyToManyField(
        "products.Product",
        blank=True,
        related_name="coupons",
        help_text="Leave empty to apply to all products",
    )
    specific_categories = models.ManyToManyField(
        "products.Category",
        blank=True,
        related_name="coupons",
        help_text="Leave empty to apply to all categories",
    )

    class Meta:
        verbose_name = "Coupon"
        verbose_name_plural = "Coupons"
        ordering = ["-created_at"]

    def __str__(self):
        return self.code

    @property
    def is_valid(self):
        """
        Check if coupon is currently valid.
        Verifica se o cupom é válido atualmente.
        """
        now = timezone.now()

        if not self.is_active:
            return False

        if self.valid_from and now < self.valid_from:
            return False

        if self.valid_until and now > self.valid_until:
            return False

        if self.usage_limit and self.times_used >= self.usage_limit:
            return False

        return True

    def can_use(self, user, order_value):
        """
        Check if user can use this coupon.
        Verifica se o usuário pode usar este cupom.
        """
        if not self.is_valid:
            return False, "Coupon is not valid."

        if order_value < self.min_order_value:
            return False, f"Minimum order value is R$ {self.min_order_value}."

        if self.first_purchase_only:
            from apps.orders.models import Order

            if Order.objects.filter(user=user).exists():
                return False, "This coupon is for first purchase only."

        # Check per-user limit
        # Verifica limite por usuário
        user_usage = CouponUsage.objects.filter(coupon=self, user=user).count()
        if user_usage >= self.usage_limit_per_user:
            return False, "You have already used this coupon."

        return True, None

    def calculate_discount(self, order_value):
        """
        Calculate discount amount.
        Calcula o valor do desconto.
        """
        if self.discount_type == "percentage":
            discount = order_value * (self.discount_value / 100)
            if self.max_discount:
                discount = min(discount, self.max_discount)
            return discount
        else:
            return min(self.discount_value, order_value)


class CouponUsage(models.Model):
    """
    Track coupon usage by users.
    Rastreia o uso de cupons pelos usuários.
    """

    coupon = models.ForeignKey(
        Coupon,
        on_delete=models.CASCADE,
        related_name="usages",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="coupon_usages",
    )
    order = models.ForeignKey(
        "orders.Order",
        on_delete=models.SET_NULL,
        null=True,
        related_name="coupon_usages",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Coupon Usage"
        verbose_name_plural = "Coupon Usages"

    def __str__(self):
        return f"{self.user.email} used {self.coupon.code}"
