"""
Audit models for the E-commerce Backend.
Modelos de auditoria para o Backend E-commerce.
"""

from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from apps.core.models import TimeStampedModel


class AuditLog(TimeStampedModel):
    """
    Audit log for tracking changes.
    Log de auditoria para rastrear alterações.
    """

    ACTION_CHOICES = [
        ("create", "Create"),
        ("update", "Update"),
        ("delete", "Delete"),
        ("login", "Login"),
        ("logout", "Logout"),
        ("export", "Export"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_logs",
    )
    action = models.CharField(
        "Action",
        max_length=20,
        choices=ACTION_CHOICES,
        db_index=True,
    )

    # What was affected
    # O que foi afetado
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey("content_type", "object_id")
    object_repr = models.CharField("Object", max_length=255, blank=True)

    # Change details
    # Detalhes da alteração
    changes = models.JSONField("Changes", null=True, blank=True)

    # Request info
    # Informações da requisição
    ip_address = models.GenericIPAddressField("IP Address", null=True, blank=True)
    user_agent = models.CharField("User Agent", max_length=500, blank=True)

    class Meta:
        verbose_name = "Audit Log"
        verbose_name_plural = "Audit Logs"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["action", "created_at"]),
            models.Index(fields=["user", "created_at"]),
        ]

    def __str__(self):
        user_str = self.user.email if self.user else "System"
        return f"{user_str} {self.action} {self.object_repr}"


def log_action(
    user,
    action: str,
    obj=None,
    changes: dict = None,
    request=None,
):
    """
    Helper to create audit log entries.
    Auxiliar para criar entradas de log de auditoria.
    """
    content_type = None
    object_id = None
    object_repr = ""

    if obj:
        content_type = ContentType.objects.get_for_model(obj)
        object_id = obj.pk
        object_repr = str(obj)[:255]

    ip_address = None
    user_agent = ""

    if request:
        ip_address = request.META.get("REMOTE_ADDR")
        user_agent = request.META.get("HTTP_USER_AGENT", "")[:500]

    AuditLog.objects.create(
        user=user,
        action=action,
        content_type=content_type,
        object_id=object_id,
        object_repr=object_repr,
        changes=changes,
        ip_address=ip_address,
        user_agent=user_agent,
    )
