"""
Serializers for the products app.
"""

from rest_framework import serializers

from .models import Brand, Category, Product, ProductImage, ProductReview, ProductVariation, Stock


class CategorySerializer(serializers.ModelSerializer):
    """
    Serializer for product categories.
    """

    children = serializers.SerializerMethodField()
    full_path = serializers.ReadOnlyField()

    class Meta:
        model = Category
        fields = [
            "id",
            "name",
            "slug",
            "description",
            "image",
            "is_active",
            "parent",
            "children",
            "full_path",
            "meta_title",
            "meta_description",
        ]

    def get_children(self, obj):
        """Get child categories."""
        children = obj.get_children().filter(is_active=True)
        return CategorySerializer(children, many=True).data


class CategoryTreeSerializer(serializers.ModelSerializer):
    """
    Simplified category serializer for tree view.
    """

    children = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ["id", "name", "slug", "children"]

    def get_children(self, obj):
        children = obj.get_children().filter(is_active=True)
        return CategoryTreeSerializer(children, many=True).data


class BrandSerializer(serializers.ModelSerializer):
    """
    Serializer for product brands.
    """

    class Meta:
        model = Brand
        fields = [
            "id",
            "name",
            "slug",
            "logo",
            "description",
            "website",
        ]


class ProductImageSerializer(serializers.ModelSerializer):
    """
    Serializer for product images.
    """

    class Meta:
        model = ProductImage
        fields = ["id", "image", "alt_text", "is_primary", "order"]


class ProductVariationSerializer(serializers.ModelSerializer):
    """
    Serializer for product variations.
    """

    full_sku = serializers.ReadOnlyField()
    final_price = serializers.ReadOnlyField()
    available_quantity = serializers.SerializerMethodField()

    class Meta:
        model = ProductVariation
        fields = [
            "id",
            "name",
            "sku_suffix",
            "full_sku",
            "attributes",
            "price_modifier",
            "final_price",
            "is_active",
            "available_quantity",
        ]

    def get_available_quantity(self, obj):
        """Get available stock for this variation."""
        stock = obj.stock_items.first()
        return stock.available_quantity if stock else 0


class StockSerializer(serializers.ModelSerializer):
    """
    Serializer for stock information.
    """

    available_quantity = serializers.ReadOnlyField()
    is_low_stock = serializers.ReadOnlyField()
    is_in_stock = serializers.ReadOnlyField()

    class Meta:
        model = Stock
        fields = [
            "id",
            "quantity",
            "reserved_quantity",
            "available_quantity",
            "low_stock_threshold",
            "is_low_stock",
            "is_in_stock",
            "location",
        ]


class ProductListSerializer(serializers.ModelSerializer):
    """
    Simplified product serializer for list views.
    """

    category_name = serializers.CharField(source="category.name", read_only=True)
    brand_name = serializers.CharField(source="brand.name", read_only=True)
    current_price = serializers.ReadOnlyField()
    discount_percentage = serializers.ReadOnlyField()
    is_on_sale = serializers.ReadOnlyField()
    primary_image = ProductImageSerializer(read_only=True)
    average_rating = serializers.ReadOnlyField()
    total_stock = serializers.ReadOnlyField()

    class Meta:
        model = Product
        fields = [
            "id",
            "sku",
            "name",
            "slug",
            "short_description",
            "category",
            "category_name",
            "brand_name",
            "base_price",
            "sale_price",
            "current_price",
            "discount_percentage",
            "is_on_sale",
            "is_featured",
            "primary_image",
            "average_rating",
            "total_stock",
        ]


class ProductDetailSerializer(serializers.ModelSerializer):
    """
    Full product serializer for detail views.
    """

    category = CategorySerializer(read_only=True)
    brand = BrandSerializer(read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    variations = ProductVariationSerializer(many=True, read_only=True)
    current_price = serializers.ReadOnlyField()
    discount_percentage = serializers.ReadOnlyField()
    is_on_sale = serializers.ReadOnlyField()
    average_rating = serializers.ReadOnlyField()
    total_stock = serializers.ReadOnlyField()
    review_count = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id",
            "sku",
            "name",
            "slug",
            "description",
            "short_description",
            "category",
            "brand",
            "base_price",
            "sale_price",
            "current_price",
            "discount_percentage",
            "is_on_sale",
            "is_active",
            "is_featured",
            "weight",
            "length",
            "width",
            "height",
            "meta_title",
            "meta_description",
            "images",
            "variations",
            "average_rating",
            "review_count",
            "total_stock",
            "view_count",
            "created_at",
        ]

    def get_review_count(self, obj):
        return obj.reviews.filter(is_approved=True).count()


class ProductReviewSerializer(serializers.ModelSerializer):
    """
    Serializer for product reviews.
    """

    user_name = serializers.CharField(source="user.full_name", read_only=True)

    class Meta:
        model = ProductReview
        fields = [
            "id",
            "user_name",
            "rating",
            "title",
            "comment",
            "is_verified_purchase",
            "created_at",
        ]
        read_only_fields = ["id", "user_name", "is_verified_purchase", "created_at"]


class ProductReviewCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating product reviews.
    """

    class Meta:
        model = ProductReview
        fields = ["rating", "title", "comment"]

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        validated_data["product"] = self.context["product"]
        return super().create(validated_data)


# Admin Serializers
class ProductAdminSerializer(serializers.ModelSerializer):
    """
    Admin serializer for product management.
    """

    class Meta:
        model = Product
        fields = "__all__"


class StockUpdateSerializer(serializers.Serializer):
    """
    Serializer for stock updates.
    """

    quantity = serializers.IntegerField(min_value=0)
    action = serializers.ChoiceField(choices=["set", "add", "subtract"])

    def update(self, instance, validated_data):
        action = validated_data["action"]
        quantity = validated_data["quantity"]

        if action == "set":
            instance.quantity = quantity
        elif action == "add":
            instance.quantity += quantity
        elif action == "subtract":
            instance.quantity = max(0, instance.quantity - quantity)

        instance.save()
        return instance
