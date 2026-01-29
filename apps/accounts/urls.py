"""
URL patterns for the accounts app.
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    AddressViewSet,
    AdminUserViewSet,
    CustomTokenObtainPairView,
    LGPDConsentUpdateView,
    LGPDDeleteView,
    LGPDExportView,
    LogoutView,
    MeView,
    PasswordChangeView,
    PasswordResetConfirmView,
    PasswordResetRequestView,
    ProfileView,
    RegisterView,
    VerifyEmailView,
)

router = DefaultRouter()
router.register("addresses", AddressViewSet, basename="address")

admin_router = DefaultRouter()
admin_router.register("users", AdminUserViewSet, basename="admin-user")

urlpatterns = [
    # Authentication
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", CustomTokenObtainPairView.as_view(), name="login"),
    path("refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("logout/", LogoutView.as_view(), name="logout"),
    # Email verification
    path("verify-email/", VerifyEmailView.as_view(), name="verify_email"),
    # Password management
    path("password/change/", PasswordChangeView.as_view(), name="password_change"),
    path(
        "password/reset/",
        PasswordResetRequestView.as_view(),
        name="password_reset_request",
    ),
    path(
        "password/reset/confirm/",
        PasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    # User profile
    path("me/", MeView.as_view(), name="me"),
    path("profile/", ProfileView.as_view(), name="profile"),
    # Addresses
    path("", include(router.urls)),
    # LGPD Compliance
    path("lgpd/export/", LGPDExportView.as_view(), name="lgpd_export"),
    path("lgpd/delete/", LGPDDeleteView.as_view(), name="lgpd_delete"),
    path("lgpd/consent/", LGPDConsentUpdateView.as_view(), name="lgpd_consent"),
    # Admin
    path("admin/", include(admin_router.urls)),
]
