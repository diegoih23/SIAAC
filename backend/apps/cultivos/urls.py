from rest_framework.routers import DefaultRouter

from .views import CropViewSet, ZoneViewSet

router = DefaultRouter()
router.register("crops", CropViewSet, basename="crop")
router.register("zones", ZoneViewSet, basename="zone")

urlpatterns = router.urls
