"""Servicio principal: captura de cámara IR + inferencia YOLO + envío al backend.

Ejecución:
    cd hardware/raspberry_pi
    python services/detection_service.py
"""
import logging
import time
from datetime import datetime
from pathlib import Path

import cv2
from ultralytics import YOLO

from api_client import send_detection
from config import (
    CAMERA_HEIGHT,
    CAMERA_INDEX,
    CAMERA_WIDTH,
    COOLDOWN_SECONDS,
    EVIDENCE_DIR,
    FPS,
    SAVE_EVIDENCE,
    YOLO_CLASSES,
    YOLO_CONFIDENCE,
    YOLO_DEVICE,
    YOLO_WEIGHTS,
)

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s %(message)s")
logger = logging.getLogger("detector")

EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)


def open_camera() -> cv2.VideoCapture:
    capture = cv2.VideoCapture(CAMERA_INDEX)
    capture.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_WIDTH)
    capture.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_HEIGHT)
    capture.set(cv2.CAP_PROP_FPS, FPS)
    if not capture.isOpened():
        raise RuntimeError(f"No se pudo abrir la cámara {CAMERA_INDEX}")
    return capture


def draw(frame, detections):
    for det in detections:
        x1, y1, x2, y2 = map(int, det["bbox"])
        label = f"{det['class']} {det['confidence']:.0%}"
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 220, 0), 2)
        cv2.putText(frame, label, (x1, max(y1 - 8, 14)), cv2.FONT_HERSHEY_SIMPLEX,
                    0.55, (0, 220, 0), 2, cv2.LINE_AA)
    return frame


def main() -> None:
    logger.info("Cargando modelo %s en %s", YOLO_WEIGHTS, YOLO_DEVICE)
    model = YOLO(YOLO_WEIGHTS)
    capture = open_camera()
    last_sent: dict[str, float] = {}

    try:
        while True:
            ok, frame = capture.read()
            if not ok:
                logger.warning("Frame no disponible; reintentando…")
                time.sleep(0.5)
                continue

            results = model.predict(
                frame, conf=YOLO_CONFIDENCE, device=YOLO_DEVICE, verbose=False
            )
            detections = []
            for result in results:
                for box in result.boxes:
                    name = result.names[int(box.cls[0])]
                    if YOLO_CLASSES and name not in YOLO_CLASSES:
                        continue
                    detections.append(
                        {
                            "class": name,
                            "confidence": float(box.conf[0]),
                            "bbox": [round(float(v), 1) for v in box.xyxy[0].tolist()],
                        }
                    )

            annotated = draw(frame.copy(), detections)
            cv2.imshow("SIAAC - Detección", annotated)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

            for det in detections:
                now = time.time()
                if now - last_sent.get(det["class"], 0) < COOLDOWN_SECONDS:
                    continue
                last_sent[det["class"]] = now

                image_path = None
                if SAVE_EVIDENCE:
                    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    image_path = str(EVIDENCE_DIR / f"{stamp}_{det['class']}.jpg")
                    cv2.imwrite(image_path, annotated)
                send_detection(det["class"], det["confidence"], det["bbox"], image_path)

            time.sleep(max(1.0 / max(FPS, 1) - 0.05, 0.02))
    finally:
        capture.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
