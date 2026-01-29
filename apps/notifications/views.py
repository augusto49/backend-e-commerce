"""
Views for the notifications app.
"""

from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Notification


class NotificationListView(APIView):
    """
    Get user notifications.
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        notifications = Notification.objects.filter(user=request.user)[:50]
        data = [
            {
                "id": n.id,
                "type": n.type,
                "title": n.title,
                "message": n.message,
                "link": n.link,
                "is_read": n.is_read,
                "created_at": n.created_at,
            }
            for n in notifications
        ]
        unread_count = Notification.objects.filter(
            user=request.user, is_read=False
        ).count()
        return Response(
            {"success": True, "data": data, "unread_count": unread_count}
        )


class MarkNotificationReadView(APIView):
    """
    Mark notification as read.
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, notification_id):
        try:
            notification = Notification.objects.get(
                id=notification_id,
                user=request.user,
            )
            notification.mark_as_read()
            return Response({"success": True, "message": "Notification marked as read."})
        except Notification.DoesNotExist:
            return Response(
                {"success": False, "message": "Notification not found."},
                status=404,
            )


class MarkAllReadView(APIView):
    """
    Mark all notifications as read.
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        from django.utils import timezone

        Notification.objects.filter(
            user=request.user,
            is_read=False,
        ).update(is_read=True, read_at=timezone.now())

        return Response({"success": True, "message": "All notifications marked as read."})
