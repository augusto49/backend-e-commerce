"""
Product models for the E-commerce Backend.
"""

from decimal import Decimal

from django.db import models
from django.utils.text import slugify
from mptt.models import MPTTModel, TreeForeignKey

from apps.core.models import BaseModel, TimeStampedModel


class Category(MPTTModel, TimeStampedModel):
    """
    Product categories with hierarchical structure using MPTT.
    """

    name = models.CharField("Name", max_length=200)
    slug = models.SlugField("Slug", max_length=220, unique=True)
    parent = TreeForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="children",
    )
    description = models.TextField("Description", blank=True)
    image = models.ImageField(
        "Image",
        upload_to="categories/%Y/%m/",
        null=True,
        blank=True,
    )
    is_active = models.BooleanField("Active", default=True)
    order = models.PositiveIntegerField("Order", default=0)

    # SEO
    meta_title = models.CharField("Meta Title", max_length=60, blank=True)
    meta_description = models.CharField("Meta Description", max_length=160, blank=True)

    class MPTTMeta:
        order_insertion_by = ["order", "name"]

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"
        ordering = ["order", "name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    @property
    def full_path(self):
        """Return the full category path."""
        ancestors = self.get_ancestors(include_self=True)
        return " > ".join([a.name for a in ancestors])


class Brand(TimeStampedModel):
    """
    Product brands.
    """

    name = models.CharField("Name", max_length=200)
    slug = models.SlugField("Slug", max_length=220, unique=True)
    logo = models.ImageField(
        "Logo",
        upload_to="brands/",
        null=True,
        blank=True,
    )
    description = models.TextField("Description", blank=True)
    website = models.URLField("Website", blank=True)
    is_active = models.BooleanField("Active", default=True)

    class Meta:
        verbose_name = "Brand"
        verbose_name_plural = "Brands"
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Product(BaseModel):
    """
    Main product model.
    """

    # Basic info
    sku = models.CharField("SKU", max_length=50, unique=True)
    name = models.CharField("Name", max_length=255)
    slug = models.SlugField("Slug", max_length=280, unique=True)
    description = models.TextField("Description", blank=True)
    short_description = models.CharField(
        "Short Description",
        max_length=500,
        blank=True,
    )

    # Relations
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name="products",
    )
    brand = models.ForeignKey(
        Brand,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="products",
    )

    # Pricing
    base_price = models.DecimalField(
        "Base Price",
        max_digits=10,
        decimal_places=2,
    )
    sale_price = models.DecimalField(
        "Sale Price",
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
    )
    cost_price = models.DecimalField(
        "Cost Price",
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
    )

    # Status
    is_active = models.BooleanField("Active", default=True)
    is_featured = models.BooleanField("Featured", default=False)

    # Physical attributes
    weight = models.DecimalField(
        "Weight (kg)",
        max_digits=8,
        decimal_places=3,
        null=True,
        blank=True,
    )
    length = models.DecimalField(
        "Length (cm)",
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
    )
    width = models.DecimalField(
        "Width (cm)",
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
    )
    height = models.DecimalField(
        "Height (cm)",
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
    )

    # SEO
    meta_title = models.CharField("Meta Title", max_length=60, blank=True)
    meta_description = models.CharField("Meta Description", max_length=160, blank=True)

    # Stats
    view_count = models.PositiveIntegerField("View Count", default=0)
    order_count = models.PositiveIntegerField("Order Count", default=0)

    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["sku"]),
            models.Index(fields=["slug"]),
            models.Index(fields=["is_active", "is_featured"]),
            models.Index(fields=["category", "is_active"]),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    @property
    def current_price(self):
        """Return the current price (sale or base)."""
        return self.sale_price if self.sale_price else self.base_price

    @property
    def discount_percentage(self):
        """Return the discount percentage."""
        if self.sale_price and self.base_price > 0:
            discount = ((self.base_price - self.sale_price) / self.base_price) * 100
            return int(discount)
        return 0

    @property
    def is_on_sale(self):
        """Check if product is on sale."""
        return self.sale_price is not None and self.sale_price < self.base_price

    @property
    def primary_image(self):
        """Get the primary product image."""
        return self.images.filter(is_primary=True).first()

    @property
    def average_rating(self):
        """Calculate average rating from reviews."""
        from django.db.models import Avg

        result = self.reviews.filter(is_approved=True).aggregate(avg=Avg("rating"))
        return result["avg"] or 0

    @property
    def total_stock(self):
        """Calculate total available stock."""
        return sum(
            stock.available_quantity
            for stock in self.stock_items.all()
        )


class ProductVariation(BaseModel):
    """
    Product variations (e.g., size, color).
    """

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="variations",
    )
    sku_suffix = models.CharField(
        "SKU Suffix",
        max_length=20,
        blank=True,
    )
    name = models.CharField(
        "Variation Name",
        max_length=100,
        help_text="E.g., 'Blue - Size M'",
    )
    attributes = models.JSONField(
        "Attributes",
        default=dict,
        help_text='E.g., {"color": "blue", "size": "M"}',
    )
    price_modifier = models.DecimalField(
        "Price Modifier",
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text="Amount to add/subtract from base price",
    )
    is_active = models.BooleanField("Active", default=True)

    class Meta:
        verbose_name = "Product Variation"
        verbose_name_plural = "Product Variations"
        ordering = ["name"]
        unique_together = ["product", "name"]

    def __str__(self):
        return f"{self.product.name} - {self.name}"

    @property
    def full_sku(self):
        """Return the full SKU including product SKU."""
        return f"{self.product.sku}-{self.sku_suffix}" if self.sku_suffix else self.product.sku

    @property
    def final_price(self):
        """Calculate the final price with modifier."""
        base = self.product.current_price
        return base + self.price_modifier


class ProductImage(TimeStampedModel):
    """
    Product images.
    """

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="images",
    )
    image = models.ImageField(
        "Image",
        upload_to="products/%Y/%m/",
    )
    alt_text = models.CharField("Alt Text", max_length=255, blank=True)
    is_primary = models.BooleanField("Primary Image", default=False)
    order = models.PositiveIntegerField("Order", default=0)

    class Meta:
        verbose_name = "Product Image"
        verbose_name_plural = "Product Images"
        ordering = ["order", "-is_primary"]

    def __str__(self):
        return f"Image for {self.product.name}"

    def save(self, *args, **kwargs):
        if self.is_primary:
            ProductImage.objects.filter(
                product=self.product,
                is_primary=True,
            ).exclude(pk=self.pk).update(is_primary=False)
        super().save(*args, **kwargs)


class Stock(TimeStampedModel):
    """
    Stock management for products and variations.
    """

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="stock_items",
    )
    variation = models.ForeignKey(
        ProductVariation,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="stock_items",
    )
    quantity = models.PositiveIntegerField("Quantity", default=0)
    reserved_quantity = models.PositiveIntegerField(
        "Reserved Quantity",
        default=0,
        help_text="Stock reserved for pending orders",
    )
    low_stock_threshold = models.PositiveIntegerField(
        "Low Stock Threshold",
        default=10,
    )
    location = models.CharField(
        "Storage Location",
        max_length=100,
        blank=True,
    )

    class Meta:
        verbose_name = "Stock"
        verbose_name_plural = "Stock Items"
        unique_together = ["product", "variation"]

    def __str__(self):
        if self.variation:
            return f"Stock for {self.product.name} - {self.variation.name}"
        return f"Stock for {self.product.name}"

    @property
    def available_quantity(self):
        """Return the available quantity (total - reserved)."""
        return max(0, self.quantity - self.reserved_quantity)

    @property
    def is_low_stock(self):
        """Check if stock is below threshold."""
        return self.available_quantity <= self.low_stock_threshold

    @property
    def is_in_stock(self):
        """Check if item is in stock."""
        return self.available_quantity > 0


class ProductReview(BaseModel):
    """
    Product reviews and ratings.
    """

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="reviews",
    )
    user = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="product_reviews",
    )
    rating = models.PositiveSmallIntegerField(
        "Rating",
        choices=[(i, str(i)) for i in range(1, 6)],
    )
    title = models.CharField("Title", max_length=200)
    comment = models.TextField("Comment")
    is_approved = models.BooleanField("Approved", default=False)
    is_verified_purchase = models.BooleanField(
        "Verified Purchase",
        default=False,
    )

    class Meta:
        verbose_name = "Product Review"
        verbose_name_plural = "Product Reviews"
        ordering = ["-created_at"]
        unique_together = ["product", "user"]

    def __str__(self):
        return f"Review by {self.user.email} for {self.product.name}"
