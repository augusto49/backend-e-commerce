"""
Serializers for the coupons app.
"""

from rest_framework import serializers

from .models import Coupon


class CouponSerializer(serializers.ModelSerializer):
    """
    Serializer for coupons.
    """

    is_valid = serializers.ReadOnlyField()

    class Meta:
        model = Coupon
        fields = [
            "id",
            "code",
            "description",
            "discount_type",
            "discount_value",
            "max_discount",
            "min_order_value",
            "is_valid",
            "valid_until",
        ]


class CouponValidateSerializer(serializers.Serializer):
    """
    Serializer for validating a coupon.
    """

    code = serializers.CharField(max_length=50)
    order_value = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        default=0,
    )


class CouponAdminSerializer(serializers.ModelSerializer):
    """
    Admin serializer for coupon management.
    Serializer administrativo para gestão de cupons.
    """

    usages_count = serializers.SerializerMethodField()

    class Meta:
        model = Coupon
        fields = [
            "id",
            "code",
            "description",
            "discount_type",
            "discount_value",
            "max_discount",
            "min_order_value",
            "usage_limit",
            "usage_limit_per_user",
            "times_used",
            "usages_count",
            "is_active",
            "valid_from",
            "valid_until",
            "first_purchase_only",
            "specific_products",
            "specific_categories",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "times_used", "usages_count", "created_at", "updated_at"]

    def get_usages_count(self, obj):
        """Get total usage count."""
        return obj.usages.count()
