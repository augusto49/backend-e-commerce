"""
URL patterns for the shipping app.
"""

from django.urls import path

from .views import CalculateShippingView, TrackShipmentView

urlpatterns = [
    path("calculate/", CalculateShippingView.as_view(), name="shipping_calculate"),
    path("track/<str:tracking_code>/", TrackShipmentView.as_view(), name="shipping_track"),
]
