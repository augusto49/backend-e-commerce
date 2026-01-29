"""
URL patterns for the shipping app.
Padrões de URL para o app de envio/frete.
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    CalculateShippingView,
    ShippingMethodAdminViewSet,
    ShippingRateAdminViewSet,
    TrackShipmentView,
)

admin_router = DefaultRouter()
admin_router.register("methods", ShippingMethodAdminViewSet, basename="admin-shipping-method")
admin_router.register("rates", ShippingRateAdminViewSet, basename="admin-shipping-rate")

urlpatterns = [
    path("calculate/", CalculateShippingView.as_view(), name="shipping_calculate"),
    path("track/<str:tracking_code>/", TrackShipmentView.as_view(), name="shipping_track"),
    path("admin/", include(admin_router.urls)),
]

