"""
Serializers for the wishlist app.
"""

from rest_framework import serializers

from apps.products.serializers import ProductListSerializer

from .models import WishlistItem


class WishlistItemSerializer(serializers.ModelSerializer):
    """
    Serializer for wishlist items.
    """

    product = ProductListSerializer(read_only=True)

    class Meta:
        model = WishlistItem
        fields = ["id", "product", "created_at"]


class WishlistAddSerializer(serializers.Serializer):
    """
    Serializer for adding to wishlist.
    """

    product_id = serializers.IntegerField()
