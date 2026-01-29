"""
URL patterns for the cart app.
"""

from django.urls import path

from .views import CartClearView, CartCouponView, CartItemDetailView, CartItemView, CartView

urlpatterns = [
    path("", CartView.as_view(), name="cart"),
    path("items/", CartItemView.as_view(), name="cart_add_item"),
    path("items/<int:item_id>/", CartItemDetailView.as_view(), name="cart_item_detail"),
    path("coupon/", CartCouponView.as_view(), name="cart_coupon"),
    path("clear/", CartClearView.as_view(), name="cart_clear"),
]
