"""
Webhooks models for the E-commerce Backend.
Modelos de Webhooks para o Backend E-commerce.
"""

import hashlib
import hmac
import json
import logging
import requests

from django.db import models

from apps.core.models import BaseModel, TimeStampedModel

logger = logging.getLogger(__name__)


class WebhookEndpoint(BaseModel):
    """
    Webhook endpoints for external integrations.
    Endpoints de webhook para integrações externas.
    """

    name = models.CharField("Name", max_length=100)
    url = models.URLField("URL")
    secret = models.CharField("Secret", max_length=255)
    is_active = models.BooleanField("Active", default=True)

    # Events to send
    # Eventos para enviar
    events = models.JSONField(
        "Events",
        default=list,
        help_text="List of event types to send",
    )

    # Headers
    # Cabeçalhos (Headers)
    custom_headers = models.JSONField(
        "Custom Headers",
        default=dict,
        blank=True,
    )

    class Meta:
        verbose_name = "Webhook Endpoint"
        verbose_name_plural = "Webhook Endpoints"

    def __str__(self):
        return self.name

    def send(self, event_type: str, payload: dict):
        """
        Send webhook to endpoint.
        Envia webhook para o endpoint.
        """
        if not self.is_active:
            return False

        if self.events and event_type not in self.events:
            return False

        # Generate signature
        # Gera assinatura (signature)
        payload_str = json.dumps(payload, sort_keys=True)
        signature = hmac.new(
            self.secret.encode(),
            payload_str.encode(),
            hashlib.sha256,
        ).hexdigest()

        headers = {
            "Content-Type": "application/json",
            "X-Webhook-Signature": signature,
            "X-Event-Type": event_type,
            **self.custom_headers,
        }

        try:
            response = requests.post(
                self.url,
                json=payload,
                headers=headers,
                timeout=10,
            )

            # Log delivery
            # Registra entrega (log)
            WebhookDelivery.objects.create(
                endpoint=self,
                event_type=event_type,
                payload=payload,
                status_code=response.status_code,
                response_body=response.text[:1000],
                success=response.status_code < 400,
            )

            return response.status_code < 400

        except Exception as e:
            logger.exception(f"Webhook delivery failed: {e}")
            WebhookDelivery.objects.create(
                endpoint=self,
                event_type=event_type,
                payload=payload,
                status_code=0,
                response_body=str(e),
                success=False,
            )
            return False


class WebhookDelivery(TimeStampedModel):
    """
    Track webhook deliveries.
    Rastreia entregas de webhook.
    """

    endpoint = models.ForeignKey(
        WebhookEndpoint,
        on_delete=models.CASCADE,
        related_name="deliveries",
    )
    event_type = models.CharField("Event Type", max_length=100)
    payload = models.JSONField("Payload")
    status_code = models.PositiveIntegerField("Status Code")
    response_body = models.TextField("Response", blank=True)
    success = models.BooleanField("Success")

    class Meta:
        verbose_name = "Webhook Delivery"
        verbose_name_plural = "Webhook Deliveries"
        ordering = ["-created_at"]


def trigger_webhook(event_type: str, payload: dict):
    """
    Trigger webhooks for an event.
    Dispara webhooks para um evento.
    """
    endpoints = WebhookEndpoint.objects.filter(is_active=True)

    for endpoint in endpoints:
        endpoint.send(event_type, payload)
