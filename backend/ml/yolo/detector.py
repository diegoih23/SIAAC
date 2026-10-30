"""Servicio de inferencia YOLO reutilizable por el backend y la Raspberry Pi."""
from __future__ import annotations

import logging
from pathlib import Path

import cv2
import numpy as np

logger = logging.getLogger(__name__)


class YoloDetector:
    """Singleton que mantiene el modelo cargado en memoria (una sola instancia)."""

    _instance: "YoloDetector | None" = None
    _model = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, weights: str = "yolo11n.pt", device: str = "cpu", confidence: float = 0.45):
        self.weights = weights
        self.device = device
        self.confidence = confidence

    def load(self):
        if self._model is None:
            from ultralytics import YOLO

            logger.info("Cargando modelo YOLO: %s en %s", self.weights, self.device)
            self._model = YOLO(self.weights)
        return self._model

    def predict(self, source, conf: float | None = None, classes: list[int] | None = None) -> list[dict]:
        """Ejecuta inferencia sobre una ruta, frame numpy o PIL.Image."""
        model = self.load()
        results = model.predict(
            source=source,
            conf=conf if conf is not None else self.confidence,
            device=self.device,
            classes=classes,
            verbose=False,
        )
        detections: list[dict] = []
        for result in results:
            names = result.names
            for box in result.boxes:
                x1, y1, x2, y2 = [round(float(v), 2) for v in box.xyxy[0].tolist()]
                class_id = int(box.cls[0])
                detections.append(
                    {
                        "class_id": class_id,
                        "object_class": names.get(class_id, str(class_id)),
                        "confidence": round(float(box.conf[0]), 4),
                        "bbox": [x1, y1, x2, y2],
                    }
                )
        return detections

    def annotated_frame(self, frame: np.ndarray, detections: list[dict]) -> np.ndarray:
        """Dibuja cajas y etiquetas sobre el frame (para streaming MJPEG)."""
        output = frame.copy()
        for det in detections:
            x1, y1, x2, y2 = map(int, det["bbox"])
            label = f"{det['object_class']} {det['confidence']:.0%}"
            cv2.rectangle(output, (x1, y1), (x2, y2), (0, 200, 0), 2)
            cv2.putText(
                output, label, (x1, max(y1 - 8, 12)),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 200, 0), 2, cv2.LINE_AA,
            )
        return output

    def process_image(self, image_path: str, output_path: str | None = None) -> list[dict]:
        detections = self.predict(image_path)
        if output_path:
            frame = cv2.imread(image_path)
            cv2.imwrite(output_path, self.annotated_frame(frame, detections))
        return detections


def get_detector() -> YoloDetector:
    """Construye el detector con la configuración de Django si está disponible."""
    try:
        from django.conf import settings

        return YoloDetector(settings.YOLO_MODEL_PATH, settings.YOLO_DEVICE, settings.YOLO_CONFIDENCE)
    except Exception:
        return YoloDetector()


if __name__ == "__main__":
    import argparse
    import json

    parser = argparse.ArgumentParser(description="Prueba local del detector YOLO")
    parser.add_argument("image", help="Ruta de la imagen a analizar")
    parser.add_argument("--weights", default="ml/yolo/weights/yolo11n.pt")
    parser.add_argument("--output", default=None)
    args = parser.parse_args()

    detector = YoloDetector(args.weights)
    print(json.dumps(detector.process_image(args.image, args.output), indent=2, ensure_ascii=False))
