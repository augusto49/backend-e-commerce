"""
Serializers for the accounts app.
"""

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.utils import timezone
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from apps.core.utils import validate_cpf

from .models import Address, Profile

User = get_user_model()


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom JWT token serializer that includes user data.
    """

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token["email"] = user.email
        token["user_type"] = user.user_type
        token["full_name"] = user.full_name

        return token

    def validate(self, attrs):
        data = super().validate(attrs)

        # Add user data to response
        data["user"] = {
            "id": self.user.id,
            "email": self.user.email,
            "full_name": self.user.full_name,
            "user_type": self.user.user_type,
            "is_verified": self.user.is_verified,
        }

        return data


class RegisterSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.
    """

    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={"input_type": "password"},
    )
    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        style={"input_type": "password"},
    )
    lgpd_consent = serializers.BooleanField(required=True)

    class Meta:
        model = User
        fields = [
            "email",
            "password",
            "password_confirm",
            "first_name",
            "last_name",
            "cpf",
            "phone",
            "lgpd_consent",
        ]

    def validate_cpf(self, value):
        """Validate CPF format and uniqueness."""
        if value:
            # Remove formatting
            cpf_clean = "".join(filter(str.isdigit, value))
            if not validate_cpf(cpf_clean):
                raise serializers.ValidationError("Invalid CPF number.")
            if User.objects.filter(cpf=cpf_clean).exists():
                raise serializers.ValidationError("CPF already registered.")
            return cpf_clean
        return value

    def validate_lgpd_consent(self, value):
        """Ensure LGPD consent is provided."""
        if not value:
            raise serializers.ValidationError(
                "You must accept the LGPD terms to register."
            )
        return value

    def validate(self, attrs):
        """Validate password confirmation."""
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError(
                {"password_confirm": "Passwords do not match."}
            )
        return attrs

    def create(self, validated_data):
        """Create a new user."""
        validated_data.pop("password_confirm")
        lgpd_consent = validated_data.pop("lgpd_consent")

        user = User.objects.create_user(
            email=validated_data["email"],
            password=validated_data["password"],
            first_name=validated_data.get("first_name", ""),
            last_name=validated_data.get("last_name", ""),
            cpf=validated_data.get("cpf"),
            phone=validated_data.get("phone", ""),
            lgpd_consent=lgpd_consent,
            lgpd_consent_date=timezone.now() if lgpd_consent else None,
        )

        return user


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for user details.
    """

    full_name = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "full_name",
            "cpf",
            "phone",
            "user_type",
            "is_verified",
            "date_joined",
        ]
        read_only_fields = ["id", "email", "user_type", "is_verified", "date_joined"]


class UserUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating user information.
    """

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "phone",
        ]


class ProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for user profile.
    """

    class Meta:
        model = Profile
        fields = [
            "birth_date",
            "avatar",
            "newsletter_opt_in",
            "sms_opt_in",
        ]


class AddressSerializer(serializers.ModelSerializer):
    """
    Serializer for user addresses.
    """

    full_address = serializers.ReadOnlyField()

    class Meta:
        model = Address
        fields = [
            "id",
            "name",
            "recipient_name",
            "street",
            "number",
            "complement",
            "neighborhood",
            "city",
            "state",
            "zipcode",
            "country",
            "address_type",
            "is_default",
            "phone",
            "full_address",
        ]
        read_only_fields = ["id"]

    def validate_zipcode(self, value):
        """Validate and normalize zipcode."""
        zipcode = "".join(filter(str.isdigit, value))
        if len(zipcode) != 8:
            raise serializers.ValidationError("Invalid ZIP code.")
        return zipcode

    def create(self, validated_data):
        """Create address with user from context."""
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)


class PasswordChangeSerializer(serializers.Serializer):
    """
    Serializer for password change.
    """

    old_password = serializers.CharField(
        required=True,
        style={"input_type": "password"},
    )
    new_password = serializers.CharField(
        required=True,
        validators=[validate_password],
        style={"input_type": "password"},
    )
    new_password_confirm = serializers.CharField(
        required=True,
        style={"input_type": "password"},
    )

    def validate_old_password(self, value):
        """Validate current password."""
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("Current password is incorrect.")
        return value

    def validate(self, attrs):
        """Validate password confirmation."""
        if attrs["new_password"] != attrs["new_password_confirm"]:
            raise serializers.ValidationError(
                {"new_password_confirm": "Passwords do not match."}
            )
        return attrs


class PasswordResetRequestSerializer(serializers.Serializer):
    """
    Serializer for password reset request.
    """

    email = serializers.EmailField(required=True)


class PasswordResetConfirmSerializer(serializers.Serializer):
    """
    Serializer for password reset confirmation.
    """

    token = serializers.CharField(required=True)
    new_password = serializers.CharField(
        required=True,
        validators=[validate_password],
        style={"input_type": "password"},
    )
    new_password_confirm = serializers.CharField(
        required=True,
        style={"input_type": "password"},
    )

    def validate(self, attrs):
        """Validate password confirmation."""
        if attrs["new_password"] != attrs["new_password_confirm"]:
            raise serializers.ValidationError(
                {"new_password_confirm": "Passwords do not match."}
            )
        return attrs


class LGPDExportSerializer(serializers.ModelSerializer):
    """
    Serializer for LGPD data export.
    """

    addresses = AddressSerializer(many=True, read_only=True)
    profile = ProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "cpf",
            "phone",
            "user_type",
            "is_verified",
            "lgpd_consent",
            "lgpd_consent_date",
            "date_joined",
            "addresses",
            "profile",
        ]
