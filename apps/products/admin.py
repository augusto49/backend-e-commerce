"""
Admin configuration for the products app.
"""

from django.contrib import admin
from mptt.admin import DraggableMPTTAdmin

from .models import Brand, Category, Product, ProductImage, ProductReview, ProductVariation, Stock


@admin.register(Category)
class CategoryAdmin(DraggableMPTTAdmin):
    list_display = [
        "tree_actions",
        "indented_title",
        "slug",
        "is_active",
        "order",
    ]
    list_display_links = ["indented_title"]
    list_filter = ["is_active"]
    search_fields = ["name", "slug"]
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "is_active"]
    list_filter = ["is_active"]
    search_fields = ["name"]
    prepopulated_fields = {"slug": ("name",)}


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


class ProductVariationInline(admin.TabularInline):
    model = ProductVariation
    extra = 1


class StockInline(admin.TabularInline):
    model = Stock
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        "sku",
        "name",
        "category",
        "base_price",
        "sale_price",
        "is_active",
        "is_featured",
        "total_stock",
    ]
    list_filter = ["is_active", "is_featured", "category", "brand"]
    search_fields = ["name", "sku", "description"]
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ["view_count", "order_count"]
    inlines = [ProductImageInline, ProductVariationInline, StockInline]

    fieldsets = (
        (None, {"fields": ("sku", "name", "slug")}),
        ("Description", {"fields": ("short_description", "description")}),
        ("Classification", {"fields": ("category", "brand")}),
        (
            "Pricing",
            {"fields": ("base_price", "sale_price", "cost_price")},
        ),
        ("Status", {"fields": ("is_active", "is_featured")}),
        (
            "Dimensions",
            {
                "fields": ("weight", "length", "width", "height"),
                "classes": ("collapse",),
            },
        ),
        (
            "SEO",
            {
                "fields": ("meta_title", "meta_description"),
                "classes": ("collapse",),
            },
        ),
        (
            "Stats",
            {
                "fields": ("view_count", "order_count"),
                "classes": ("collapse",),
            },
        ),
    )


@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    list_display = [
        "product",
        "user",
        "rating",
        "is_approved",
        "is_verified_purchase",
        "created_at",
    ]
    list_filter = ["is_approved", "rating", "is_verified_purchase"]
    search_fields = ["product__name", "user__email", "title"]
    actions = ["approve_reviews", "reject_reviews"]

    def approve_reviews(self, request, queryset):
        queryset.update(is_approved=True)

    approve_reviews.short_description = "Approve selected reviews"

    def reject_reviews(self, request, queryset):
        queryset.update(is_approved=False)

    reject_reviews.short_description = "Reject selected reviews"


@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = [
        "product",
        "variation",
        "quantity",
        "reserved_quantity",
        "available_quantity",
        "is_low_stock",
    ]
    list_filter = ["product__category"]
    search_fields = ["product__name", "product__sku"]
