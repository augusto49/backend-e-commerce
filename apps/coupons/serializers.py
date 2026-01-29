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
