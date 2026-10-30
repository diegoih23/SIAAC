# Detalle de módulos

## Módulo 1 - Autenticación y sesión de usuarios

**Backend:** `backend/apps/autenticacion` · **Frontend:** `frontend/src/modules/autenticacion`

- Registro, login JWT, refresh y logout.
- Roles `ADMIN`, `OPERATOR`, `VIEWER`.
- Perfil, cambio de contraseña y avatar.
- Registro de sesiones (`UserSession`) con IP, agente y cierre remoto.
- `GET /api/v1/auth/me/` devuelve el usuario autenticado.

**Modelos:** `User`, `UserSession`.

**Frontend:** pantalla de login, perfil, cierre de sesión y adjunto del token
en cada petición (Axios interceptor).

---

## Módulo 2 - Gestión de cultivos y zonas

**Backend:** `backend/apps/cultivos` · **Frontend:** `frontend/src/modules/cultivos`

- CRUD de cultivos con estado fenológico y fechas de siembra/cosecha.
- CRUD de zonas georreferenciadas (latitud, longitud, área, responsable).
- Una zona agrupa dispositivos, cámaras, reglas y reportes.
- Borrado lógico de zonas para no perder trazabilidad.

**Modelos:** `Crop`, `Zone`.

**Frontend:** tablas de cultivos y tarjetas de zonas con estado y contadores.

---

## Módulo 3 - Monitoreo en tiempo real

**Backend:** `backend/apps/monitoreo` · **Frontend:** `frontend/src/modules/monitoreo`

- Ingesta de lecturas de sensores del ESP32 (`PIR`, temperatura, humedad, suelo, luz).
- WebSocket por zona (`/ws/monitoring/zones/<id>/`) y global (`/ws/monitoring/`).
- Gestión de cámaras y solicitud de captura.
- Endpoint `latest` con la última lectura por sensor y zona.

**Modelos:** `Camera`, `SensorReading`.

**Frontend:** tarjetas por zona con lecturas en vivo, estado de conexión y feed
de eventos recientes.

---

## Módulo 4 - Supervisión y reportes

**Backend:** `backend/apps/reportes` · **Frontend:** `frontend/src/modules/reportes`

- Tablero con indicadores de 24 horas (zonas, cultivos, detecciones, dispositivos).
- Generación de reportes PDF/CSV por tipo, zona y periodo.
- Historial de reportes y regeneración.
- Vistas SQL de apoyo: `vw_detecciones_por_zona`, `vw_estado_dispositivos`.

**Modelo:** `Report`.

**Frontend:** dashboard con gráfica de clases detectadas y página de reportes con
descarga de archivos.

---

## Módulo 5 - Configuración y respuesta disuasiva

**Backend:** `backend/apps/respuestas` · **Frontend:** `frontend/src/modules/respuestas`

- Reglas por zona: clases YOLO, confianza mínima, ventana horaria, acción y duración.
- Acciones: `SIREN`, `LIGHT`, `BOTH`.
- Activación automática al registrarse un evento compatible o manual desde la UI.
- Envío de comandos por MQTT al ESP32 y registro de cada activación.

**Modelos:** `DisuasiveRule`, `DisuasionActivation`.

**Frontend:** tarjetas de reglas, activación de prueba e historial de comandos.

---

## Módulo 6 - Gestión de notificaciones

**Backend:** `backend/apps/notificaciones` · **Frontend:** `frontend/src/modules/notificaciones`

- Bandeja por usuario con categoría, prioridad y estado leído.
- Notificaciones automáticas al detectar objetos (ADMIN/OPERATOR).
- Canales previstos: in-app, correo, push y SMS.
- Preferencias por categoría/canal y horas de silencio.
- WebSocket por usuario (`/ws/notifications/`).

**Modelos:** `Notification`, `NotificationPreference`.

**Frontend:** bandeja con contador de no leídas y actualización por WebSocket.

---

## Detección automática (Hardware e IA)

**Backend:** `backend/apps/deteccion` + `backend/ml/yolo` ·
**Frontend:** `frontend/src/modules/deteccion` · **Hardware:** `hardware/`

- Registro de dispositivos (ESP32, Raspberry Pi, cámaras) con API key.
- Catálogo de modelos YOLO con umbral de confianza y clases.
- Ingesta de eventos con imagen, bbox y confianza desde la Raspberry Pi.
- Revisión de eventos: verificado, falso positivo o atendido.
- Estadísticas por clase y difusión en tiempo real.
- Servicio `YoloDetector` reutilizable y CLI de prueba.

**Modelos:** `Device`, `AIModel`, `DetectionEvent`.

**Hardware:**
- `hardware/esp32/firmware` (PlatformIO): PIR, sirena, luces, HTTP y MQTT.
- `hardware/raspberry_pi/services`: captura, YOLO, envío de eventos y MQTT.
