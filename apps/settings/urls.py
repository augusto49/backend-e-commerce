"""
URL patterns for the settings app.
Padrões de URL para o app de configurações.
"""

from django.urls import path

from .views import PublicStoreSettingsView, StoreSettingsDetailView

urlpatterns = [
    path("", StoreSettingsDetailView.as_view(), name="settings_detail"),
    path("public/", PublicStoreSettingsView.as_view(), name="settings_public"),
]
