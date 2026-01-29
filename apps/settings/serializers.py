"""
Serializers for the settings app.
Serializers para o app de configurações.
"""

from rest_framework import serializers

from .models import StoreSettings


class StoreSettingsSerializer(serializers.ModelSerializer):
    """
    Serializer for store settings.
    Serializer para configurações da loja.
    """

    class Meta:
        model = StoreSettings
        fields = [
            "id",
            # Store Information
            "store_name",
            "store_description",
            "logo",
            "favicon",
            # Business Information
            "cnpj",
            "razao_social",
            "state_registration",
            # Contact Information
            "email",
            "phone",
            "whatsapp",
            # Address
            "address_street",
            "address_number",
            "address_complement",
            "address_neighborhood",
            "address_city",
            "address_state",
            "address_zipcode",
            # Social Media
            "instagram",
            "facebook",
            "twitter",
            "youtube",
            "tiktok",
            # Policies
            "terms_of_service",
            "privacy_policy",
            "return_policy",
            "shipping_policy",
            # SEO
            "meta_title",
            "meta_description",
            "meta_keywords",
            # Configuration
            "currency",
            "timezone",
            "maintenance_mode",
            "allow_guest_checkout",
            # Email Settings
            "email_from_name",
            "email_from_address",
            # Timestamps
            "updated_at",
        ]
        read_only_fields = ["id", "updated_at"]


class StoreSettingsPublicSerializer(serializers.ModelSerializer):
    """
    Public serializer for store settings (limited fields).
    Serializer público para configurações da loja (campos limitados).
    """

    class Meta:
        model = StoreSettings
        fields = [
            "store_name",
            "store_description",
            "logo",
            "favicon",
            "email",
            "phone",
            "whatsapp",
            "instagram",
            "facebook",
            "twitter",
            "youtube",
            "tiktok",
            "terms_of_service",
            "privacy_policy",
            "return_policy",
            "shipping_policy",
            "currency",
        ]
