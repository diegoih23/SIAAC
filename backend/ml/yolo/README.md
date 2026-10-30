# Detección de objetos (YOLO)

Servicio de inferencia compartido entre el backend y la Raspberry Pi.

## Estructura

```
ml/yolo/
├── detector.py          # Clase YoloDetector + CLI de prueba
└── weights/             # Pesos .pt (no versionados)
    └── .gitkeep
```

## Colocar los pesos

1. Descarga un modelo preentrenado (`yolo11n.pt`, `yolov8n.pt`, etc.) o entrena uno propio
   con las clases del cultivo (persona, animal, vehículo, etc.).
2. Copia el archivo en `ml/yolo/weights/`.
3. Ajusta `YOLO_MODEL_PATH`, `YOLO_CONFIDENCE` y `YOLO_DEVICE` en `backend/.env`.

## Prueba rápida

```bash
cd backend
source .venv/bin/activate
python -m ml.yolo.detector ruta/foto.jpg --output /tmp/detectado.jpg
```

## Entrenamiento (opcional)

```bash
yolo detect train data=dataset/data.yaml model=yolo11n.pt epochs=100 imgsz=640
```

> En Raspberry Pi se recomienda exportar a NCNN/ONNX o usar `yolo11n` para mantener
> una inferencia fluida; un modelo más grande puede ejecutarse en el servidor.
