"""
Serializers for the audit app.
Serializers para o app de auditoria.
"""

from rest_framework import serializers

from .models import AuditLog


class AuditLogSerializer(serializers.ModelSerializer):
    """
    Serializer for audit logs.
    Serializer para logs de auditoria.
    """

    user_email = serializers.CharField(source="user.email", read_only=True, default="System")
    content_type_name = serializers.CharField(source="content_type.model", read_only=True)

    class Meta:
        model = AuditLog
        fields = [
            "id",
            "user",
            "user_email",
            "action",
            "content_type",
            "content_type_name",
            "object_id",
            "object_repr",
            "changes",
            "ip_address",
            "user_agent",
            "created_at",
        ]
        read_only_fields = fields
