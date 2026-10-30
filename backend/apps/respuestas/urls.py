from rest_framework.routers import DefaultRouter

from .views import DisuasionActivationViewSet, DisuasiveRuleViewSet

router = DefaultRouter()
router.register("rules", DisuasiveRuleViewSet, basename="disuasive-rule")
router.register("activations", DisuasionActivationViewSet, basename="disuasion-activation")

urlpatterns = router.urls
