"""Rutas raíz de la API SIAAC (v1)."""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework_simplejwt.views import TokenRefreshView

from apps.autenticacion.views import SiaacTokenObtainPairView

api_v1_patterns = [
    # Módulo 1: Autenticación y sesión
    path("auth/", include("apps.autenticacion.urls")),
    path("auth/token/", SiaacTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    # Módulo 2: Cultivos y zonas
    path("crops/", include("apps.cultivos.urls")),
    # Módulo 3: Monitoreo en tiempo real
    path("monitoring/", include("apps.monitoreo.urls")),
    # Módulo 4: Supervisión y reportes
    path("reports/", include("apps.reportes.urls")),
    # Módulo 5: Configuración y respuesta disuasiva
    path("disuasion/", include("apps.respuestas.urls")),
    # Módulo 6: Notificaciones
    path("notifications/", include("apps.notificaciones.urls")),
    # Detección automática (hardware + IA)
    path("detection/", include("apps.deteccion.urls")),
]

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/", include(api_v1_patterns)),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
