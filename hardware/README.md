# Hardware del prototipo SIAAC

## Lista de materiales (BOM)

| Cantidad | Componente | Función |
| --- | --- | --- |
| 1 | ESP32 DevKit V1 | Nodo de sensores y actuadores. |
| 1 | Sensor PIR HC-SR501 | Detección de movimiento. |
| 1 | Bocina / sirena 5–12 V + relé | Respuesta disuasiva sonora. |
| 1 | Luz LED / reflector 12 V + relé | Respuesta disuasiva luminosa. |
| 1 | Raspberry Pi 4 (2 GB+) | Procesamiento de imágenes y YOLO. |
| 1 | Cámara IR-CUT 1080p | Visión nocturna infrarroja. |
| 1 | Fuente 12 V 3 A + regulador 5 V 3 A | Alimentación del prototipo. |
| 2 | Módulos relé 1 canal | Aislamiento de cargas. |
| 1 | Protoboard / PCB y cableado | Montaje. |
| — | Fusible, diodos 1N4007, resistencias | Protección eléctrica. |

## Distribución de funciones

```
ESP32:
  - PIR (GPIO 27)
  - Bocina / sirena (GPIO 26 vía relé)
  - Luz disuasiva (GPIO 25 vía relé)
  - WiFi + HTTP + MQTT

Raspberry Pi:
  - Cámara IR-CUT
  - Modelo YOLO
  - Envío de eventos al backend
  - (Opcional) MQTT para actuadores locales
```

## Alimentación

- Fuente principal de **12 V 3 A** con fusible.
- Regulador **LM2596** ajustado a 5 V para ESP32, PIR y cámara.
- Relés para conmutar sirena y luces de 12 V.
- GND común entre fuente, ESP32, PIR y relés.
- No alimentar la sirena desde el pin GPIO ni desde el USB de la Raspberry Pi.

## Documentación

- `esp32/docs/wiring.md`: tabla de pines, diagrama y recomendaciones.
- `esp32/firmware/`: proyecto PlatformIO listo para compilar.
- `raspberry_pi/README.md`: instalación del servicio de detección.
