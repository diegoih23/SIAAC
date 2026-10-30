from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (
    AIModelViewSet,
    DetectionEventViewSet,
    DetectionIngestView,
    DeviceViewSet,
)

router = DefaultRouter()
router.register("devices", DeviceViewSet, basename="device")
router.register("models", AIModelViewSet, basename="ai-model")
router.register("events", DetectionEventViewSet, basename="detection-event")

urlpatterns = [
    path("events/ingest/", DetectionIngestView.as_view(), name="detection-ingest"),
    *router.urls,
]
