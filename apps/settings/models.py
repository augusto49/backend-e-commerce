"""
Store settings models for the E-commerce Backend.
Modelos de configurações da loja para o Backend E-commerce.
"""

from django.db import models

from apps.core.models import TimeStampedModel


class StoreSettings(TimeStampedModel):
    """
    Singleton model for store settings.
    Modelo singleton para configurações da loja.
    """

    # Store Information
    # Informações da Loja
    store_name = models.CharField("Store Name", max_length=200, default="My Store")
    store_description = models.TextField("Store Description", blank=True)
    logo = models.ImageField("Logo", upload_to="settings/", null=True, blank=True)
    favicon = models.ImageField("Favicon", upload_to="settings/", null=True, blank=True)

    # Business Information
    # Informações Comerciais
    cnpj = models.CharField("CNPJ", max_length=18, blank=True)
    razao_social = models.CharField("Razão Social", max_length=200, blank=True)
    state_registration = models.CharField("Inscrição Estadual", max_length=20, blank=True)

    # Contact Information
    # Informações de Contato
    email = models.EmailField("Email", blank=True)
    phone = models.CharField("Phone", max_length=20, blank=True)
    whatsapp = models.CharField("WhatsApp", max_length=20, blank=True)

    # Address
    # Endereço
    address_street = models.CharField("Street", max_length=200, blank=True)
    address_number = models.CharField("Number", max_length=20, blank=True)
    address_complement = models.CharField("Complement", max_length=100, blank=True)
    address_neighborhood = models.CharField("Neighborhood", max_length=100, blank=True)
    address_city = models.CharField("City", max_length=100, blank=True)
    address_state = models.CharField("State", max_length=2, blank=True)
    address_zipcode = models.CharField("ZIP Code", max_length=9, blank=True)

    # Social Media
    # Redes Sociais
    instagram = models.URLField("Instagram", blank=True)
    facebook = models.URLField("Facebook", blank=True)
    twitter = models.URLField("Twitter/X", blank=True)
    youtube = models.URLField("YouTube", blank=True)
    tiktok = models.URLField("TikTok", blank=True)

    # Store Policies
    # Políticas da Loja
    terms_of_service = models.TextField("Terms of Service", blank=True)
    privacy_policy = models.TextField("Privacy Policy", blank=True)
    return_policy = models.TextField("Return Policy", blank=True)
    shipping_policy = models.TextField("Shipping Policy", blank=True)

    # SEO
    meta_title = models.CharField("Meta Title", max_length=60, blank=True)
    meta_description = models.CharField("Meta Description", max_length=160, blank=True)
    meta_keywords = models.CharField("Meta Keywords", max_length=255, blank=True)

    # Configuration
    # Configurações
    currency = models.CharField(
        "Currency",
        max_length=3,
        default="BRL",
        choices=[
            ("BRL", "Brazilian Real"),
            ("USD", "US Dollar"),
            ("EUR", "Euro"),
        ],
    )
    timezone = models.CharField("Timezone", max_length=50, default="America/Sao_Paulo")
    maintenance_mode = models.BooleanField("Maintenance Mode", default=False)
    allow_guest_checkout = models.BooleanField("Allow Guest Checkout", default=True)

    # Email Settings
    # Configurações de Email
    email_from_name = models.CharField("Email From Name", max_length=100, blank=True)
    email_from_address = models.EmailField("Email From Address", blank=True)

    class Meta:
        verbose_name = "Store Settings"
        verbose_name_plural = "Store Settings"

    def __str__(self):
        return self.store_name

    def save(self, *args, **kwargs):
        """
        Ensure only one instance exists (Singleton pattern).
        Garante que apenas uma instância exista (padrão Singleton).
        """
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """
        Prevent deletion of settings.
        Previne exclusão das configurações.
        """
        pass

    @classmethod
    def get_settings(cls):
        """
        Get or create the settings instance.
        Obtém ou cria a instância de configurações.
        """
        settings, _ = cls.objects.get_or_create(pk=1)
        return settings
