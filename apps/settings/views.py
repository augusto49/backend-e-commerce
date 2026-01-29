"""
Views for the settings app.
Views para o app de configurações.
"""

from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.permissions import IsAdminUser

from .models import StoreSettings
from .serializers import StoreSettingsPublicSerializer, StoreSettingsSerializer


class StoreSettingsDetailView(APIView):
    """
    Get or update store settings.
    Obtém ou atualiza configurações da loja.
    """

    permission_classes = [IsAdminUser]

    def get(self, request):
        settings = StoreSettings.get_settings()
        serializer = StoreSettingsSerializer(settings)
        return Response({"success": True, "data": serializer.data})

    def patch(self, request):
        settings = StoreSettings.get_settings()
        serializer = StoreSettingsSerializer(settings, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {
                "success": True,
                "message": "Settings updated successfully.",
                "data": serializer.data,
            }
        )


class PublicStoreSettingsView(APIView):
    """
    Get public store settings.
    Obtém configurações públicas da loja.
    """

    permission_classes = [permissions.AllowAny]

    def get(self, request):
        settings = StoreSettings.get_settings()
        serializer = StoreSettingsPublicSerializer(settings)
        return Response({"success": True, "data": serializer.data})
