"""
Serializers for the orders app.
"""

from rest_framework import serializers

from apps.products.serializers import ProductListSerializer

from .models import Order, OrderItem, OrderStatusHistory


class OrderItemSerializer(serializers.ModelSerializer):
    """
    Serializer for order items.
    """

    product = ProductListSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = [
            "id",
            "product",
            "product_name",
            "product_sku",
            "variation_name",
            "quantity",
            "unit_price",
            "total_price",
        ]


class OrderStatusHistorySerializer(serializers.ModelSerializer):
    """
    Serializer for order status history.
    """

    created_by_email = serializers.CharField(
        source="created_by.email",
        read_only=True,
    )

    class Meta:
        model = OrderStatusHistory
        fields = ["id", "status", "notes", "created_by_email", "created_at"]


class OrderListSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for order list.
    """

    item_count = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            "id",
            "number",
            "status",
            "total",
            "item_count",
            "created_at",
        ]

    def get_item_count(self, obj):
        return obj.items.count()


class OrderDetailSerializer(serializers.ModelSerializer):
    """
    Full serializer for order details.
    """

    items = OrderItemSerializer(many=True, read_only=True)
    status_history = OrderStatusHistorySerializer(many=True, read_only=True)
    can_cancel = serializers.ReadOnlyField()

    class Meta:
        model = Order
        fields = [
            "id",
            "number",
            "status",
            "shipping_address",
            "billing_address",
            "subtotal",
            "shipping_cost",
            "discount",
            "total",
            "coupon_code",
            "shipping_method",
            "tracking_code",
            "estimated_delivery",
            "customer_notes",
            "items",
            "status_history",
            "can_cancel",
            "created_at",
            "updated_at",
        ]


class CheckoutSerializer(serializers.Serializer):
    """
    Serializer for checkout.
    """

    shipping_address_id = serializers.IntegerField()
    billing_address_id = serializers.IntegerField(required=False)
    shipping_method = serializers.CharField(max_length=100)
    payment_method = serializers.CharField(max_length=50)
    customer_notes = serializers.CharField(required=False, allow_blank=True)


class OrderStatusUpdateSerializer(serializers.Serializer):
    """
    Serializer for updating order status (admin).
    """

    status = serializers.ChoiceField(choices=Order.STATUS_CHOICES)
    notes = serializers.CharField(required=False, allow_blank=True)
    tracking_code = serializers.CharField(required=False, allow_blank=True)
