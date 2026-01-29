"""
URL patterns for the orders app.
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CheckoutView, OrderAdminViewSet, OrderViewSet

router = DefaultRouter()
router.register("", OrderViewSet, basename="order")

admin_router = DefaultRouter()
admin_router.register("", OrderAdminViewSet, basename="admin-order")

urlpatterns = [
    path("checkout/", CheckoutView.as_view(), name="checkout"),
    # Admin routes MUST come before the catch-all router
    path("admin/", include(admin_router.urls)),
    path("", include(router.urls)),
]
