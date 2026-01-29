"""
URL patterns for the notifications app.
"""

from django.urls import path

from .views import MarkAllReadView, MarkNotificationReadView, NotificationListView

urlpatterns = [
    path("", NotificationListView.as_view(), name="notification_list"),
    path("<int:notification_id>/read/", MarkNotificationReadView.as_view(), name="notification_read"),
    path("read-all/", MarkAllReadView.as_view(), name="notification_read_all"),
]
