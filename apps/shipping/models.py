"""
Shipping models for the E-commerce Backend.
Modelos de envio/frete para o Backend E-commerce.
"""

from decimal import Decimal

from django.db import models

from apps.core.models import BaseModel, TimeStampedModel


class ShippingMethod(BaseModel):
    """
    Shipping methods available.
    Métodos de envio disponíveis.
    """

    name = models.CharField("Name", max_length=100)
    code = models.CharField("Code", max_length=50, unique=True)
    carrier = models.CharField(
        "Carrier",
        max_length=50,
        choices=[
            ("correios", "Correios"),
            ("jadlog", "JadLog"),
            ("custom", "Custom"),
        ],
    )
    description = models.TextField("Description", blank=True)
    is_active = models.BooleanField("Active", default=True)

    # Pricing
    # Precificação
    base_price = models.DecimalField(
        "Base Price",
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    # Delivery time
    # Tempo de entrega
    min_days = models.PositiveIntegerField("Minimum Days", default=1)
    max_days = models.PositiveIntegerField("Maximum Days", default=7)

    class Meta:
        verbose_name = "Shipping Method"
        verbose_name_plural = "Shipping Methods"
        ordering = ["name"]

    def __str__(self):
        return self.name


class ShippingRate(TimeStampedModel):
    """
    Shipping rates by region.
    Taxas de envio por região.
    """

    method = models.ForeignKey(
        ShippingMethod,
        on_delete=models.CASCADE,
        related_name="rates",
    )
    zipcode_start = models.CharField("CEP Start", max_length=8)
    zipcode_end = models.CharField("CEP End", max_length=8)
    price = models.DecimalField(
        "Price",
        max_digits=10,
        decimal_places=2,
    )
    additional_per_kg = models.DecimalField(
        "Additional per Kg",
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    class Meta:
        verbose_name = "Shipping Rate"
        verbose_name_plural = "Shipping Rates"

    def __str__(self):
        return f"{self.method.name}: {self.zipcode_start}-{self.zipcode_end}"
