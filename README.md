# SIAAC

**Sistema Inteligente de Alerta de Animales en Cultivos**

SIAAC es un prototipo de monitoreo agrícola que detecta animales mediante
fotografías, sensores y visión artificial. El sistema registra los eventos,
los relaciona con una zona de cultivo y los muestra en una aplicación web.

## 1. Estructura del proyecto

```text
SIAAC/
├── backend/                         # API Django + REST
│   ├── apps/autenticacion/          # Usuarios, roles, JWT, sesiones y 2FA
│   ├── apps/cultivos/               # Cultivos, zonas y asignaciones
│   ├── apps/deteccion/              # Dispositivos, eventos y YOLO
│   ├── apps/monitoreo/              # Lecturas y monitoreo
│   ├── ml/yolo/                     # Detector YOLO + pesos locales
│   ├── media/                       # Imágenes y archivos generados
│   ├── manage.py
│   └── requirements.txt
├── frontend/                        # React + Vite
│   └── src/modules/                 # Módulos de la aplicación
├── hardware/
│   ├── esp32/                       # Firmware del nodo ESP32
│   └── raspberry_pi/                # Servicios de captura y envío
├── database/                        # schema.sql y seed.sql
├── deploy/                          # Configuración de Nginx
├── docker-compose.yml
└── Makefile
```

## 2. Requisitos

- Python 3.11 o superior.
- Node.js 18 o superior y npm.
- MariaDB 10.6+ o Docker.
- Redis para WebSockets.
- Git.
- Opcional: PlatformIO para el ESP32.
- Opcional: Raspberry Pi con cámara.

## 3. Configuración inicial

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate                 # Linux/macOS
# .venv\Scripts\activate                  # Windows
pip install -r requirements.txt
cp .env.example .env
```

Configura en `backend/.env` la base de datos, Redis, JWT y YOLO.
Nunca publiques este archivo.

### Frontend

```bash
cd frontend
npm install
cp .env.example .env
```

La configuración básica usa:

```env
VITE_API_URL=/api/v1
VITE_WS_URL=ws://localhost:8000
```

## 4. Ejecutar cada parte por separado

### 4.1 Base de datos y Redis

Con Docker:

```bash
docker compose up -d db redis
```

O utiliza servicios locales y completa sus datos en `backend/.env`.

### 4.2 Backend Django

```bash
cd backend
source .venv/bin/activate
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```

API disponible en:

```text
http://localhost:8000/api/v1/
```

Documentación interactiva:

```text
http://localhost:8000/api/docs/
```

Crear un administrador:

```bash
python manage.py createsuperuser
```

El administrador puede gestionar cultivos, zonas, usuarios y dispositivos.

### 4.3 Frontend React

En otra terminal:

```bash
cd frontend
npm run dev
```

Aplicación disponible en:

```text
http://localhost:5173
```

Para compilar producción:

```bash
npm run build
npm run preview
```

## 5. Ejecutar con Docker

Desde la raíz:

```bash
docker compose up --build
```

Servicios:

| Servicio | URL |
|---|---|
| Frontend | http://localhost:5173 |
| Backend | http://localhost:8000 |
| Swagger | http://localhost:8000/api/docs/ |
| Adminer | http://localhost:8081 |
| MariaDB | localhost:3306 |
| Redis | localhost:6379 |

## 6. YOLO y OpenCV

El detector reconoce las cinco especies definidas para el proyecto:

- `bird` — ave
- `cow` — vaca
- `sheep` — oveja
- `dog` — perro
- `horse` — caballo

Coloca los pesos en:

```text
backend/ml/yolo/weights/yolo11n.pt
```

Para descargar el modelo base:

```bash
cd backend
source .venv/bin/activate
python -c "from ultralytics import YOLO; YOLO('yolo11n.pt')"
cp yolo11n.pt ml/yolo/weights/
```

Prueba local del detector:

```bash
python -m ml.yolo.detector test_images/Hairz.jpg \
  --weights ml/yolo/weights/yolo11n.pt \
  --output /tmp/deteccion.jpg
```

## 7. Probar una imagen mediante la API

### Analizar sin guardar evento

Obtén un token iniciando sesión en el frontend o usando:

```bash
curl -X POST http://localhost:8000/api/v1/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"TU_USUARIO","password":"TU_CONTRASEÑA"}'
```

Luego:

```bash
curl -X POST http://localhost:8000/api/v1/detection/events/analyze/ \
  -H "Authorization: Bearer TU_ACCESS_TOKEN" \
  -F "image=@backend/test_images/Hairz.jpg"
```

### Recibir una fotografía desde un dispositivo y guardar el evento

El dispositivo debe estar registrado y asociado a una zona:

```bash
curl -X POST http://localhost:8000/api/v1/detection/events/ingest/ \
  -H "X-Device-Key: API_KEY_DEL_DISPOSITIVO" \
  -F "device_serial=ESP32-SIAAC-001" \
  -F "zone=1" \
  -F "image=@backend/test_images/Hairz.jpg"
```

El backend ejecuta YOLO y guarda cada detección con su imagen, confianza,
coordenadas, zona, dispositivo y fecha.

## 8. Cultivos, zonas y dispositivos

Desde el frontend:

1. Inicia sesión con un usuario `ADMIN`.
2. Ve a **Cultivos** y registra el cultivo.
3. Ve a **Zonas**, crea una zona y selecciónala en el mapa.
4. Ve a **Dispositivos**, registra el ESP32 o Raspberry Pi.
5. Asocia el dispositivo a la zona.
6. Configura el `serial_number` y la `api_key` en el dispositivo.

Los administradores pueden asignar cultivos a otros usuarios. Los operadores
solo consultan los cultivos y zonas que tienen asignados.

## 9. Raspberry Pi

Configura:

```text
hardware/raspberry_pi/services/config.py
```

El cliente puede enviar una detección ya inferida:

```python
send_detection(object_class, confidence, bbox, image_path)
```

O enviar una fotografía para que YOLO se ejecute en el backend:

```python
send_photo_for_analysis("/ruta/a/captura.jpg")
```

Ejecutar servicios:

```bash
cd hardware/raspberry_pi
pip install -r requirements.txt
python services/detection_service.py
```

## 10. ESP32

Configura una copia local de:

```text
hardware/esp32/firmware/include/config.example.h
```

como `config.h` y completa:

- WiFi.
- IP y puerto del backend.
- Serial del dispositivo.
- API key.
- ID de zona.
- Pines del PIR, bocina y luz.

Compilar y cargar con PlatformIO:

```bash
cd hardware/esp32/firmware
pio run
pio run --target upload
pio device monitor
```

El firmware actual reporta movimiento PIR, heartbeat y comandos de
disuasión. La captura directa depende del modelo específico de cámara
ESP32-CAM y de su distribución de pines.

## 11. Pruebas

Backend:

```bash
cd backend
source .venv/bin/activate
pytest -q
```

Frontend:

```bash
cd frontend
npm run build
npm run lint
```

## 12. Seguridad y archivos no versionados

No publiques:

- `backend/.env` ni `frontend/.env`.
- Contraseñas, tokens o API keys.
- `backend/.venv/`.
- `frontend/node_modules/`.
- Archivos de producción en `media/`.
- Pesos privados o entrenados de YOLO.

Los valores públicos de ejemplo deben mantenerse únicamente en los archivos
`.env.example`.

## 13. Flujo completo del sistema

```text
PIR detecta movimiento
        ↓
Cámara toma fotografía
        ↓
ESP32/Raspberry envía imagen
        ↓
API Django valida dispositivo y zona
        ↓
OpenCV decodifica la imagen
        ↓
YOLO reconoce la especie
        ↓
Se guarda el evento y la evidencia
        ↓
Frontend muestra la detección ampliable
```
