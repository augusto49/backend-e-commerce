"""
URL patterns for the audit app.
Padrões de URL para o app de auditoria.
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import AuditLogViewSet

router = DefaultRouter()
router.register("logs", AuditLogViewSet, basename="audit-log")

urlpatterns = [
    path("", include(router.urls)),
]
