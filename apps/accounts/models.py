"""
User models for the E-commerce Backend.
Modelos de usuário para o Backend E-commerce.
"""

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models

from apps.core.models import BaseModel, TimeStampedModel


class UserManager(BaseUserManager):
    """
    Custom user manager.
    Gerenciador de usuários personalizado.
    """

    def create_user(self, email, password=None, **extra_fields):
        """
        Create and return a regular user.
        Cria e retorna um usuário regular.
        """
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Create and return a superuser.
        Cria e retorna um superusuário.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("user_type", "admin")

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """
    Custom User model that uses email as the primary identifier.
    Modelo de Usuário personalizado que usa email como identificador primário.
    """

    USER_TYPE_CHOICES = [
        ("customer", "Customer"),
        ("admin", "Administrator"),
        ("staff", "Staff"),
    ]

    # Remove username field, use email instead
    # Remove o campo username, use o email no lugar
    username = None
    email = models.EmailField("Email address", unique=True)

    # Additional fields
    # Campos adicionais
    cpf = models.CharField(
        "CPF",
        max_length=14,
        unique=True,
        null=True,
        blank=True,
        help_text="Brazilian CPF number",
    )
    phone = models.CharField(
        "Phone",
        max_length=20,
        blank=True,
        help_text="Phone number with country code",
    )
    user_type = models.CharField(
        "User Type",
        max_length=20,
        choices=USER_TYPE_CHOICES,
        default="customer",
    )

    # Verification and compliance
    # Verificação e conformidade
    is_verified = models.BooleanField(
        "Email Verified",
        default=False,
        help_text="Whether the user's email is verified",
    )
    lgpd_consent = models.BooleanField(
        "LGPD Consent",
        default=False,
        help_text="Whether the user consented to LGPD terms",
    )
    lgpd_consent_date = models.DateTimeField(
        "LGPD Consent Date",
        null=True,
        blank=True,
    )

    # Timestamps
    # Carimbos de tempo (Timestamps)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
        ordering = ["-date_joined"]

    def __str__(self):
        return self.email

    @property
    def full_name(self):
        """
        Return the user's full name.
        Retorna o nome completo do usuário.
        """
        return f"{self.first_name} {self.last_name}".strip() or self.email


class Address(BaseModel):
    """
    User address model for shipping and billing.
    Modelo de endereço do usuário para envio e cobrança.
    """

    ADDRESS_TYPE_CHOICES = [
        ("shipping", "Shipping"),
        ("billing", "Billing"),
        ("both", "Both"),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="addresses",
    )
    name = models.CharField("Address Name", max_length=100, blank=True)
    recipient_name = models.CharField("Recipient Name", max_length=200)
    street = models.CharField("Street", max_length=255)
    number = models.CharField("Number", max_length=20)
    complement = models.CharField("Complement", max_length=100, blank=True)
    neighborhood = models.CharField("Neighborhood", max_length=100)
    city = models.CharField("City", max_length=100)
    state = models.CharField("State", max_length=2)
    zipcode = models.CharField("ZIP Code", max_length=9)
    country = models.CharField("Country", max_length=2, default="BR")

    address_type = models.CharField(
        "Address Type",
        max_length=20,
        choices=ADDRESS_TYPE_CHOICES,
        default="both",
    )
    is_default = models.BooleanField("Default Address", default=False)
    phone = models.CharField("Phone", max_length=20, blank=True)

    class Meta:
        verbose_name = "Address"
        verbose_name_plural = "Addresses"
        ordering = ["-is_default", "-created_at"]

    def __str__(self):
        return f"{self.street}, {self.number} - {self.city}/{self.state}"

    def save(self, *args, **kwargs):
        # If this is the default address, unset other defaults
        if self.is_default:
            Address.objects.filter(
                user=self.user,
                is_default=True,
            ).exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)

    @property
    def full_address(self):
        """
        Return the full formatted address.
        Retorna o endereço completo formatado.
        """
        parts = [
            f"{self.street}, {self.number}",
            self.complement,
            self.neighborhood,
            f"{self.city}/{self.state}",
            self.zipcode,
        ]
        return ", ".join(filter(None, parts))


class Profile(TimeStampedModel):
    """
    Extended user profile model.
    Modelo de perfil de usuário estendido.
    """

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    birth_date = models.DateField("Birth Date", null=True, blank=True)
    avatar = models.ImageField(
        "Avatar",
        upload_to="avatars/%Y/%m/",
        null=True,
        blank=True,
    )
    newsletter_opt_in = models.BooleanField(
        "Newsletter Opt-in",
        default=False,
    )
    sms_opt_in = models.BooleanField(
        "SMS Opt-in",
        default=False,
    )

    class Meta:
        verbose_name = "Profile"
        verbose_name_plural = "Profiles"

    def __str__(self):
        return f"Profile of {self.user.email}"


# Signals to create profile on user creation
# Signals para criar perfil na criação do usuário
from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Create a profile when a new user is created.
    Cria um perfil quando um novo usuário é criado.
    """
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """
    Save the profile when the user is saved.
    Salva o perfil quando o usuário é salvo.
    """
    if hasattr(instance, "profile"):
        instance.profile.save()
