from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import CameraViewSet, SensorIngestView, SensorReadingViewSet

router = DefaultRouter()
router.register("cameras", CameraViewSet, basename="camera")
router.register("readings", SensorReadingViewSet, basename="sensor-reading")

urlpatterns = [
    path("readings/ingest/", SensorIngestView.as_view(), name="sensor-ingest"),
    *router.urls,
]
