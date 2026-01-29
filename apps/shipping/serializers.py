"""
Serializers for the shipping app.
Serializers para o app de envio/frete.
"""

from rest_framework import serializers

from .models import ShippingMethod, ShippingRate


class ShippingRateSerializer(serializers.ModelSerializer):
    """
    Serializer for shipping rates.
    Serializer para taxas de envio.
    """

    class Meta:
        model = ShippingRate
        fields = [
            "id",
            "method",
            "zipcode_start",
            "zipcode_end",
            "price",
            "additional_per_kg",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class ShippingMethodSerializer(serializers.ModelSerializer):
    """
    Serializer for shipping methods.
    Serializer para métodos de envio.
    """

    rates_count = serializers.SerializerMethodField()

    class Meta:
        model = ShippingMethod
        fields = [
            "id",
            "name",
            "code",
            "carrier",
            "description",
            "is_active",
            "base_price",
            "min_days",
            "max_days",
            "rates_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "rates_count", "created_at", "updated_at"]

    def get_rates_count(self, obj):
        """Get number of rates for this method."""
        return obj.rates.count()


class ShippingMethodDetailSerializer(ShippingMethodSerializer):
    """
    Detailed serializer for shipping methods with rates.
    Serializer detalhado para métodos de envio com taxas.
    """

    rates = ShippingRateSerializer(many=True, read_only=True)

    class Meta(ShippingMethodSerializer.Meta):
        fields = ShippingMethodSerializer.Meta.fields + ["rates"]
