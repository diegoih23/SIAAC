from rest_framework.routers import DefaultRouter

from .views import NotificationPreferenceViewSet, NotificationViewSet

router = DefaultRouter()
# Las rutas específicas deben registrarse antes del prefijo vacío para que
# "preferences/" no sea interpretado como el detalle de una notificación.
router.register("preferences", NotificationPreferenceViewSet, basename="notification-preference")
router.register("", NotificationViewSet, basename="notification")

urlpatterns = router.urls
