"""
Views for the audit app.
Views para o app de auditoria.
"""

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets

from apps.core.permissions import IsAdminUser

from .models import AuditLog
from .serializers import AuditLogSerializer


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Admin ViewSet for viewing audit logs.
    ViewSet de admin para visualização de logs de auditoria.
    """

    queryset = AuditLog.objects.all().select_related("user", "content_type")
    serializer_class = AuditLogSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["action", "user"]
    search_fields = ["object_repr", "user__email"]
    ordering_fields = ["created_at", "action"]
    ordering = ["-created_at"]
