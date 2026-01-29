"""
Serializers for the cart app.
"""

from rest_framework import serializers

from apps.products.serializers import ProductListSerializer, ProductVariationSerializer

from .models import Cart, CartItem


class CartItemSerializer(serializers.ModelSerializer):
    """
    Serializer for cart items.
    """

    product = ProductListSerializer(read_only=True)
    variation = ProductVariationSerializer(read_only=True)
    total_price = serializers.ReadOnlyField()

    class Meta:
        model = CartItem
        fields = [
            "id",
            "product",
            "variation",
            "quantity",
            "unit_price",
            "total_price",
        ]
        read_only_fields = ["id", "unit_price"]


class CartItemCreateSerializer(serializers.Serializer):
    """
    Serializer for adding items to cart.
    """

    product_id = serializers.IntegerField()
    variation_id = serializers.IntegerField(required=False, allow_null=True)
    quantity = serializers.IntegerField(min_value=1, default=1)


class CartItemUpdateSerializer(serializers.Serializer):
    """
    Serializer for updating cart item quantity.
    """

    quantity = serializers.IntegerField(min_value=1)


class CartSerializer(serializers.ModelSerializer):
    """
    Serializer for cart.
    """

    items = CartItemSerializer(many=True, read_only=True)
    subtotal = serializers.ReadOnlyField()
    discount = serializers.ReadOnlyField()
    total = serializers.ReadOnlyField()
    item_count = serializers.ReadOnlyField()
    coupon_code = serializers.CharField(
        source="coupon.code",
        read_only=True,
    )

    class Meta:
        model = Cart
        fields = [
            "id",
            "items",
            "coupon_code",
            "subtotal",
            "discount",
            "total",
            "item_count",
            "updated_at",
        ]


class ApplyCouponSerializer(serializers.Serializer):
    """
    Serializer for applying a coupon.
    """

    code = serializers.CharField(max_length=50)
