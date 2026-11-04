# Referencia de la API SIAAC

- **Base URL:** `http://localhost:8000/api/v1`
- **Swagger:** `http://localhost:8000/api/docs/`
- **OpenAPI:** `http://localhost:8000/api/schema/`
- **Formato:** JSON (multipart en cargas de imágenes)
- **Autenticación:** `Authorization: Bearer <access_token>`

## Autenticación (Módulo 1)

| Método | Ruta | Descripción |
| --- | --- | --- |
| POST | `/auth/token/` | Login; devuelve `access`, `refresh` y `user`. |
| POST | `/auth/token/refresh/` | Renueva el access token. |
| POST | `/auth/register/` | Registro público de usuario. |
| GET/PATCH | `/auth/me/` | Perfil del usuario autenticado. |
| POST | `/auth/change-password/` | Cambia la contraseña y cierra sesiones. |
| POST | `/auth/logout/` | Cierra las sesiones activas. |
| POST | `/auth/password-reset/request/` | Solicita un código OTP de recuperación. |
| POST | `/auth/password-reset/verify/` | Verifica el código OTP. |
| POST | `/auth/password-reset/confirm/` | Cambia la contraseña usando el código. |
| POST | `/auth/email-verification/verify/` | Verifica el correo del usuario registrado. |
| POST | `/auth/email-verification/resend/` | Reenvía el código de verificación del correo. |
| POST | `/auth/two-factor/verify/` | Verifica el segundo factor y entrega los JWT. |
| POST | `/auth/two-factor/toggle/` | Activa o desactiva 2FA del usuario autenticado. |
| GET/POST | `/auth/users/` | Administración de usuarios (ADMIN). |
| GET | `/auth/sessions/` | Sesiones propias (ADMIN ve todas). |
| POST | `/auth/sessions/{id}/revoke/` | Revoca una sesión. |

**Login**

```bash
curl -X POST http://localhost:8000/api/v1/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "Siaac2026*"}'
```

## Cultivos y zonas (Módulo 2)

| Método | Ruta | Descripción |
| --- | --- | --- |
| GET/POST | `/crops/crops/` | Lista / crea cultivos. |
| GET/PATCH/DELETE | `/crops/crops/{id}/` | Detalle y edición. |
| GET | `/crops/crops/{id}/zones/` | Zonas del cultivo. |
| GET/POST | `/crops/zones/` | Lista / crea zonas. |
| GET/PATCH/DELETE | `/crops/zones/{id}/` | Detalle, edición (borrado lógico). |

Filtros: `?status=GROWING`, `?crop=1`, `?is_active=true`, `?search=norte`.

## Monitoreo (Módulo 3)

| Método | Ruta | Descripción |
| --- | --- | --- |
| GET/POST | `/monitoring/cameras/` | Cámaras por zona. |
| POST | `/monitoring/cameras/{id}/snapshot/` | Solicita captura. |
| GET | `/monitoring/readings/` | Historial de lecturas. |
| GET | `/monitoring/readings/latest/` | Última lectura por sensor (`?zone=1`). |
| POST | `/monitoring/readings/ingest/` | Ingesta desde ESP32 (`X-Device-Key`). |

**Ingesta de una lectura**

```bash
curl -X POST http://localhost:8000/api/v1/monitoring/readings/ingest/ \
  -H "Content-Type: application/json" \
  -H "X-Device-Key: demo-api-key-esp32-001" \
  -d '{"zone": 1, "sensor_type": "PIR", "value": 1, "unit": "bool"}'
```

## Reportes (Módulo 4)

| Método | Ruta | Descripción |
| --- | --- | --- |
| GET | `/reports/dashboard/summary/` | Indicadores de las últimas 24 h. |
| GET/POST | `/reports/` | Historial / genera reporte. |
| POST | `/reports/{id}/regenerate/` | Regenera el archivo. |
| DELETE | `/reports/{id}/` | Elimina el reporte. |

Al crear un reporte se genera el archivo y se devuelve `file_url`.

## Respuesta disuasiva (Módulo 5)

| Método | Ruta | Descripción |
| --- | --- | --- |
| GET/POST | `/disuasion/rules/` | Reglas por zona. |
| POST | `/disuasion/rules/{id}/activate/` | Activación manual (prueba). |
| GET | `/disuasion/activations/` | Historial de comandos. |

## Notificaciones (Módulo 6)

| Método | Ruta | Descripción |
| --- | --- | --- |
| GET | `/notifications/` | Bandeja del usuario. |
| GET | `/notifications/unread_count/` | Contador de no leídas. |
| POST | `/notifications/{id}/mark_read/` | Marca una como leída. |
| POST | `/notifications/mark_all_read/` | Marca todas como leídas. |
| GET/POST | `/notifications/preferences/` | Preferencias por canal/categoría. |

## Detección automática

| Método | Ruta | Descripción |
| --- | --- | --- |
| GET/POST | `/detection/devices/` | Dispositivos y API keys. |
| POST | `/detection/devices/{id}/heartbeat/` | Latido del dispositivo. |
| GET/POST | `/detection/models/` | Catálogo de modelos YOLO. |
| GET | `/detection/events/` | Eventos de detección. |
| GET | `/detection/events/statistics/` | Totales por clase. |
| POST | `/detection/events/{id}/review/` | Verifica / falso positivo. |
| POST | `/detection/events/ingest/` | Ingesta desde Raspberry Pi. |

**Ingesta de un evento con imagen**

```bash
curl -X POST http://localhost:8000/api/v1/detection/events/ingest/ \
  -H "X-Device-Key: demo-api-key-rpi-001" \
  -F "device_serial=RPI-SIAAC-001" \
  -F "zone=1" \
  -F "object_class=person" \
  -F "confidence=0.91" \
  -F 'bbox=[120,80,400,500]' \
  -F "image=@evidencia.jpg"
```

## Canales WebSocket

| Canal | Uso |
| --- | --- |
| `ws://localhost:8000/ws/monitoring/` | Eventos globales (detecciones, dispositivos). Requiere sesión. |
| `ws://localhost:8000/ws/monitoring/zones/{id}/` | Lecturas y eventos de una zona. |
| `ws://localhost:8000/ws/notifications/` | Notificaciones del usuario autenticado. |

Ejemplo de mensaje:

```json
{
  "event": "detection.event",
  "payload": {
    "id": 12,
    "zone": 1,
    "zone_name": "Lote norte",
    "object_class": "person",
    "confidence": 0.91,
    "detected_at": "2026-10-30T03:14:00-05:00",
    "status": "NEW"
  }
}
```

## Códigos de error

| Código | Significado |
| --- | --- |
| 400 | Datos inválidos (serializer). |
| 401 | Token ausente, expirado o API key incorrecta. |
| 403 | Rol sin permiso para la acción. |
| 404 | Recurso inexistente. |
| 429 | Límite de peticiones (si se activa throttling). |

## Protección de acceso

- Después de **5 intentos fallidos**, la cuenta queda bloqueada durante 15 minutos.
- Los intentos se auditan en la tabla `intentos_acceso`.
- Los intentos exitosos reinician el contador de fallos.
- El usuario recibe un mensaje cuando la cuenta está bloqueada.
