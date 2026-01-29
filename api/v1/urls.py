"""
API v1 URL Configuration.
Configuração de URLs da API v1.
"""

from django.urls import include, path

app_name = "api_v1"

urlpatterns = [
    # Authentication
    # Autenticação
    path("auth/", include("apps.accounts.urls")),
    # Products & Categories
    # Produtos e Categorias
    path("products/", include("apps.products.urls")),
    # Cart
    # Carrinho
    path("cart/", include("apps.cart.urls")),
    # Wishlist
    # Lista de desejos
    path("wishlist/", include("apps.wishlist.urls")),
    # Coupons
    # Cupons
    path("coupons/", include("apps.coupons.urls")),
    # Orders
    # Pedidos
    path("orders/", include("apps.orders.urls")),
    # Payments
    # Pagamentos
    path("payments/", include("apps.payments.urls")),
    # Shipping
    # Envio/Frete
    path("shipping/", include("apps.shipping.urls")),
    # Notifications
    # Notificações
    path("notifications/", include("apps.notifications.urls")),
    # Analytics (Admin)
    # Análises (Admin)
    path("analytics/", include("apps.analytics.urls")),
    # Webhooks
    path("webhooks/", include("apps.webhooks.urls")),
    # Audit (Admin)
    # Auditoria (Admin)
    path("audit/", include("apps.audit.urls")),
]

