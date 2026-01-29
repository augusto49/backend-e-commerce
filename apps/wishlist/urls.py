"""
URL patterns for the wishlist app.
"""

from django.urls import path

from .views import WishlistAddView, WishlistCheckView, WishlistRemoveView, WishlistView

urlpatterns = [
    path("", WishlistView.as_view(), name="wishlist"),
    path("add/", WishlistAddView.as_view(), name="wishlist_add"),
    path("remove/<int:product_id>/", WishlistRemoveView.as_view(), name="wishlist_remove"),
    path("check/<int:product_id>/", WishlistCheckView.as_view(), name="wishlist_check"),
]
