"""
Analytics views.
"""

from datetime import timedelta

from django.db.models import Count, Sum
from django.utils import timezone
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.permissions import IsAdminUser
from apps.orders.models import Order
from apps.products.models import Product

from .models import SalesSummary


class DashboardStatsView(APIView):
    """
    Get dashboard statistics for admin.
    """

    permission_classes = [IsAdminUser]

    def get(self, request):
        today = timezone.now().date()
        month_start = today.replace(day=1)

        # Today's stats
        today_orders = Order.objects.filter(created_at__date=today)
        today_revenue = today_orders.aggregate(total=Sum("total"))["total"] or 0

        # Monthly stats
        month_orders = Order.objects.filter(created_at__date__gte=month_start)
        month_revenue = month_orders.aggregate(total=Sum("total"))["total"] or 0

        # Orders by status
        orders_by_status = (
            Order.objects.values("status")
            .annotate(count=Count("id"))
            .order_by("-count")
        )

        # Top products
        top_products = (
            Product.objects.filter(is_active=True)
            .order_by("-order_count")[:10]
            .values("id", "name", "order_count")
        )

        return Response(
            {
                "success": True,
                "data": {
                    "today": {
                        "orders": today_orders.count(),
                        "revenue": str(today_revenue),
                    },
                    "month": {
                        "orders": month_orders.count(),
                        "revenue": str(month_revenue),
                    },
                    "orders_by_status": list(orders_by_status),
                    "top_products": list(top_products),
                },
            }
        )


class SalesReportView(APIView):
    """
    Get sales report.
    """

    permission_classes = [IsAdminUser]

    def get(self, request):
        days = int(request.query_params.get("days", 30))
        start_date = timezone.now().date() - timedelta(days=days)

        summaries = SalesSummary.objects.filter(date__gte=start_date).order_by("date")

        data = [
            {
                "date": s.date.isoformat(),
                "orders": s.total_orders,
                "revenue": str(s.total_revenue),
                "items": s.total_items,
                "average_order": str(s.average_order_value),
            }
            for s in summaries
        ]

        return Response({"success": True, "data": data})
