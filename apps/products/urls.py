"""
URL patterns for the products app.
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    BrandViewSet,
    CategoryViewSet,
    ProductAdminViewSet,
    ProductViewSet,
    StockAdminViewSet,
)

router = DefaultRouter()
router.register("categories", CategoryViewSet, basename="category")
router.register("brands", BrandViewSet, basename="brand")
router.register("", ProductViewSet, basename="product")

admin_router = DefaultRouter()
admin_router.register("products", ProductAdminViewSet, basename="admin-product")
admin_router.register("stock", StockAdminViewSet, basename="admin-stock")

urlpatterns = [
    path("", include(router.urls)),
    path("admin/", include(admin_router.urls)),
]
