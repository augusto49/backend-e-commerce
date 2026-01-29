"""
Notification models for the E-commerce Backend.
"""

from django.conf import settings
from django.db import models

from apps.core.models import TimeStampedModel


class Notification(TimeStampedModel):
    """
    User notifications.
    """

    TYPE_CHOICES = [
        ("order", "Order"),
        ("payment", "Payment"),
        ("shipping", "Shipping"),
        ("promo", "Promotion"),
        ("system", "System"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    type = models.CharField("Type", max_length=20, choices=TYPE_CHOICES)
    title = models.CharField("Title", max_length=200)
    message = models.TextField("Message")
    link = models.URLField("Link", blank=True)
    is_read = models.BooleanField("Read", default=False)
    read_at = models.DateTimeField("Read At", null=True, blank=True)

    class Meta:
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} - {self.user.email}"

    def mark_as_read(self):
        from django.utils import timezone

        self.is_read = True
        self.read_at = timezone.now()
        self.save()


class NotificationTemplate(TimeStampedModel):
    """
    Email/SMS notification templates.
    """

    CHANNEL_CHOICES = [
        ("email", "Email"),
        ("sms", "SMS"),
    ]

    name = models.CharField("Name", max_length=100, unique=True)
    channel = models.CharField(
        "Channel",
        max_length=20,
        choices=CHANNEL_CHOICES,
    )
    subject = models.CharField("Subject", max_length=200, blank=True)
    body = models.TextField("Body")
    is_active = models.BooleanField("Active", default=True)

    class Meta:
        verbose_name = "Notification Template"
        verbose_name_plural = "Notification Templates"

    def __str__(self):
        return self.name
