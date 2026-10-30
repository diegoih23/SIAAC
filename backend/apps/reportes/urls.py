from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import DashboardSummaryView, ReportViewSet

router = DefaultRouter()
router.register("", ReportViewSet, basename="report")

urlpatterns = [
    path("dashboard/summary/", DashboardSummaryView.as_view(), name="dashboard-summary"),
    *router.urls,
]
