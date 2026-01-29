"""
Admin configuration for the audit app.
"""

from django.contrib import admin

from .models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ["user", "action", "object_repr", "created_at", "ip_address"]
    list_filter = ["action", "created_at", "content_type"]
    search_fields = ["user__email", "object_repr", "ip_address"]
    readonly_fields = [
        "user",
        "action",
        "content_type",
        "object_id",
        "object_repr",
        "changes",
        "ip_address",
        "user_agent",
        "created_at",
    ]
    date_hierarchy = "created_at"

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
