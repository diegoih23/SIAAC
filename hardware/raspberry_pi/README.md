# Raspberry Pi - Procesamiento de imágenes

La Raspberry Pi captura video de la cámara con visión nocturna, ejecuta el
modelo YOLO y envía los eventos al backend SIAAC.

## Requisitos

- Raspberry Pi 4 (2 GB+) o Raspberry Pi 5, Raspberry Pi OS 64 bits.
- Cámara IR-CUT / módulo compatible con `libcamera` o cámara USB.
- Python 3.11+.
- Al menos 2 GB libres para modelos y evidencias.

## Instalación

```bash
sudo apt update && sudo apt install -y python3-venv python3-opencv libgl1
cd hardware/raspberry_pi
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp config/.env.example config/.env   # ajustar IP, API key y zona
mkdir -p models evidence
cp /ruta/siaac_intrusos.pt models/
```

## Prueba

```bash
python services/detection_service.py
```

El servicio abre una ventana con las cajas dibujadas. En modo headless se puede
ejecutar por SSH y desactivar `cv2.imshow`.

## Instalar como servicio

```bash
sudo cp services/siaac-detector.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now siaac-detector
sudo journalctl -u siaac-detector -f
```

## Estructura

```
raspberry_pi/
├── config/.env.example     # variables de entorno
├── models/                 # pesos YOLO (.pt / .onnx)
├── evidence/               # capturas de evidencia (se crea al ejecutar)
├── services/
│   ├── config.py           # lectura de configuración
│   ├── api_client.py       # envío HTTP al backend
│   ├── detection_service.py# bucle cámara + YOLO
│   ├── mqtt_listener.py    # comandos disuasivos (opcional)
│   └── siaac-detector.service
└── README.md
```

## Flujo de un evento

1. La cámara captura un frame (IR activo de noche).
2. YOLO detecta un objeto y filtra por confianza/clases permitidas.
3. Se aplica un `COOLDOWN_SECONDS` por clase para no saturar el backend.
4. Se guarda la imagen en `evidence/` (opcional).
5. `POST /api/v1/detection/events/ingest/` con `X-Device-Key`.
6. El backend difunde el evento por WebSocket y evalúa las reglas disuasivas.
