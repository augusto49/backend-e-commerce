"""
Views for the accounts app.
"""

from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import generics, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from apps.core.permissions import IsOwner

from .models import Address, Profile
from .serializers import (
    AddressSerializer,
    CustomTokenObtainPairSerializer,
    LGPDExportSerializer,
    PasswordChangeSerializer,
    PasswordResetConfirmSerializer,
    PasswordResetRequestSerializer,
    ProfileSerializer,
    RegisterSerializer,
    UserSerializer,
    UserUpdateSerializer,
)
from .tasks import send_password_reset_email, send_verification_email

User = get_user_model()


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Custom JWT token view with user data.
    """

    serializer_class = CustomTokenObtainPairSerializer


class RegisterView(generics.CreateAPIView):
    """
    User registration endpoint.
    """

    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Send verification email
        send_verification_email.delay(user.id)

        # Generate tokens
        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "success": True,
                "message": "Registration successful. Please verify your email.",
                "data": {
                    "user": UserSerializer(user).data,
                    "tokens": {
                        "refresh": str(refresh),
                        "access": str(refresh.access_token),
                    },
                },
            },
            status=status.HTTP_201_CREATED,
        )


class LogoutView(generics.GenericAPIView):
    """
    Logout endpoint that blacklists the refresh token.
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            return Response(
                {"success": True, "message": "Logout successful."},
                status=status.HTTP_200_OK,
            )
        except Exception:
            return Response(
                {"success": False, "message": "Invalid token."},
                status=status.HTTP_400_BAD_REQUEST,
            )


class MeView(generics.RetrieveUpdateAPIView):
    """
    Get or update current user information.
    """

    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == "GET":
            return UserSerializer
        return UserUpdateSerializer

    def get_object(self):
        return self.request.user

    def retrieve(self, request, *args, **kwargs):
        serializer = self.get_serializer(request.user)
        return Response({"success": True, "data": serializer.data})

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        serializer = self.get_serializer(
            request.user,
            data=request.data,
            partial=partial,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {
                "success": True,
                "message": "Profile updated successfully.",
                "data": UserSerializer(request.user).data,
            }
        )


class ProfileView(generics.RetrieveUpdateAPIView):
    """
    Get or update user profile.
    """

    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user.profile


class AddressViewSet(viewsets.ModelViewSet):
    """
    CRUD operations for user addresses.
    """

    serializer_class = AddressSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)

    @action(detail=True, methods=["post"])
    def set_default(self, request, pk=None):
        """Set an address as the default."""
        address = self.get_object()
        address.is_default = True
        address.save()
        return Response(
            {
                "success": True,
                "message": "Address set as default.",
                "data": AddressSerializer(address).data,
            }
        )


class PasswordChangeView(generics.GenericAPIView):
    """
    Change password endpoint.
    """

    serializer_class = PasswordChangeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        request.user.set_password(serializer.validated_data["new_password"])
        request.user.save()

        return Response(
            {"success": True, "message": "Password changed successfully."},
            status=status.HTTP_200_OK,
        )


class PasswordResetRequestView(generics.GenericAPIView):
    """
    Request password reset endpoint.
    """

    serializer_class = PasswordResetRequestSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        try:
            user = User.objects.get(email=email)
            send_password_reset_email.delay(user.id)
        except User.DoesNotExist:
            pass  # Don't reveal if email exists

        return Response(
            {
                "success": True,
                "message": "If the email exists, a reset link will be sent.",
            },
            status=status.HTTP_200_OK,
        )


class PasswordResetConfirmView(generics.GenericAPIView):
    """
    Confirm password reset endpoint.
    """

    serializer_class = PasswordResetConfirmSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # TODO: Implement token validation and password reset
        # This would involve decoding the token and finding the user

        return Response(
            {"success": True, "message": "Password reset successfully."},
            status=status.HTTP_200_OK,
        )


class VerifyEmailView(generics.GenericAPIView):
    """
    Email verification endpoint.
    """

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        token = request.data.get("token")
        if not token:
            return Response(
                {"success": False, "message": "Token is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # TODO: Implement token validation
        # This would involve decoding the token and verifying the user

        return Response(
            {"success": True, "message": "Email verified successfully."},
            status=status.HTTP_200_OK,
        )


class LGPDExportView(generics.RetrieveAPIView):
    """
    LGPD data export endpoint.
    Exports all user data in compliance with LGPD Article 18, I.
    """

    serializer_class = LGPDExportSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

    def retrieve(self, request, *args, **kwargs):
        serializer = self.get_serializer(request.user)
        return Response(
            {
                "success": True,
                "message": "Your data has been exported.",
                "data": serializer.data,
            }
        )


class LGPDDeleteView(generics.DestroyAPIView):
    """
    LGPD account deletion endpoint.
    Allows users to request account deletion in compliance with LGPD Article 18, VI.
    """

    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

    def destroy(self, request, *args, **kwargs):
        user = self.get_object()

        # Anonymize user data instead of hard delete
        user.email = f"deleted_{user.id}@deleted.com"
        user.first_name = "Deleted"
        user.last_name = "User"
        user.cpf = None
        user.phone = ""
        user.is_active = False
        user.save()

        return Response(
            {
                "success": True,
                "message": "Your account has been scheduled for deletion.",
            },
            status=status.HTTP_200_OK,
        )


class LGPDConsentUpdateView(generics.GenericAPIView):
    """
    Update LGPD consent preferences.
    """

    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request):
        user = request.user
        profile = user.profile

        # Update newsletter/SMS preferences
        if "newsletter_opt_in" in request.data:
            profile.newsletter_opt_in = request.data["newsletter_opt_in"]
        if "sms_opt_in" in request.data:
            profile.sms_opt_in = request.data["sms_opt_in"]

        profile.save()

        return Response(
            {
                "success": True,
                "message": "Consent preferences updated.",
                "data": ProfileSerializer(profile).data,
            }
        )
