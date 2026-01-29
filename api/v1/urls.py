"""
API v1 URL Configuration.
"""

from django.urls import include, path

app_name = "api_v1"

urlpatterns = [
    # Authentication
    path("auth/", include("apps.accounts.urls")),
    # Products & Categories
    path("products/", include("apps.products.urls")),
    # Cart
    path("cart/", include("apps.cart.urls")),
    # Wishlist
    path("wishlist/", include("apps.wishlist.urls")),
    # Coupons
    path("coupons/", include("apps.coupons.urls")),
    # Orders
    path("orders/", include("apps.orders.urls")),
    # Payments
    path("payments/", include("apps.payments.urls")),
    # Shipping
    path("shipping/", include("apps.shipping.urls")),
    # Notifications
    path("notifications/", include("apps.notifications.urls")),
    # Analytics (Admin)
    path("analytics/", include("apps.analytics.urls")),
    # Webhooks
    path("webhooks/", include("apps.webhooks.urls")),
]
