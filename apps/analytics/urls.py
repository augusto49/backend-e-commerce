"""
URL patterns for the analytics app.
"""

from django.urls import path

from .views import DashboardStatsView, SalesReportView

urlpatterns = [
    path("dashboard/", DashboardStatsView.as_view(), name="analytics_dashboard"),
    path("sales/", SalesReportView.as_view(), name="analytics_sales"),
]
