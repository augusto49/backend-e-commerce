"""
Admin configuration for the webhooks app.
"""

from django.contrib import admin

from .models import WebhookDelivery, WebhookEndpoint


class WebhookDeliveryInline(admin.TabularInline):
    model = WebhookDelivery
    extra = 0
    readonly_fields = [
        "event_type",
        "status_code",
        "success",
        "created_at",
    ]
    max_num = 10


@admin.register(WebhookEndpoint)
class WebhookEndpointAdmin(admin.ModelAdmin):
    list_display = ["name", "url", "is_active", "created_at"]
    list_filter = ["is_active", "created_at"]
    search_fields = ["name", "url"]
    inlines = [WebhookDeliveryInline]


@admin.register(WebhookDelivery)
class WebhookDeliveryAdmin(admin.ModelAdmin):
    list_display = ["endpoint", "event_type", "status_code", "success", "created_at"]
    list_filter = ["success", "event_type", "created_at"]
    readonly_fields = ["endpoint", "event_type", "payload", "status_code", "response_body"]
