"""
URL patterns for the coupons app.
Padrões de URL para o app de cupons.
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CouponAdminViewSet, CouponValidateView

admin_router = DefaultRouter()
admin_router.register("", CouponAdminViewSet, basename="admin-coupon")

urlpatterns = [
    path("validate/", CouponValidateView.as_view(), name="coupon_validate"),
    path("admin/", include(admin_router.urls)),
]
