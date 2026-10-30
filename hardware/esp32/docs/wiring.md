# Conexionado del nodo ESP32

## Componentes

| Componente | Modelo sugerido | Alimentación |
| --- | --- | --- |
| Microcontrolador | ESP32 DevKit V1 | 5 V / 500 mA |
| Sensor de movimiento | HC-SR501 (PIR) | 5 V |
| Bocina / sirena | Módulo buzzer activo 5 V o relé + sirena 12 V | 5 V / 12 V |
| Luz disuasiva | LED de alta potencia o reflector 12 V vía relé | 12 V |
| Cámara nocturna | Módulo IR-CUT 1080p (conectada a la Raspberry Pi) | 5 V |
| Fuente | 12 V 3 A + regulador 5 V 3 A (LM2596) | — |

## Tabla de pines

| Señal | GPIO ESP32 | Conexión |
| --- | --- | --- |
| PIR OUT | GPIO 27 | Salida digital del HC-SR501 |
| Bocina / sirena | GPIO 26 | Base de transistor NPN (TIP120) + relé |
| Luz disuasiva | GPIO 25 | Módulo relé de 1 canal |
| LED de estado | GPIO 2 | LED integrado de la placa |
| GND común | GND | GND de todos los módulos y de la fuente |

## Recomendaciones eléctricas

1. Alimentar el ESP32 y los sensores desde una fuente de **5 V regulada**; no
   usar el puerto USB de la computadora para la sirena.
2. Usar un **relé o transistor** para la bocina y las luces: nunca conectar la
   carga directamente al GPIO (máximo ~12 mA por pin).
3. Colocar un **diodo flyback** (1N4007) en paralelo con cargas inductivas.
4. Mantener el PIR alejado de fuentes de calor y del módulo WiFi para evitar
   falsos positivos; ajustar los potenciómetros de sensibilidad y retardo.
5. Instalar un **fusible** en la línea de 12 V y una protección contra
   inversión de polaridad.
6. El PIR requiere ~30 s de calibración al encender (configurable en
   `PIR_WARMUP_MS`).

## Diagrama lógico

```
   Fuente 12V ── fusible ──┬── relé sirena ── sirena 12V
                           ├── relé luz ───── reflector 12V
                           └── LM2596 ── 5V ── ESP32 / PIR

   ESP32 GPIO26 ── R1 1kΩ ── Base TIP120 ── Bobina relé sirena
   ESP32 GPIO25 ── módulo relé luz
   ESP32 GPIO27 ── PIR OUT
   GND común en todos los módulos
```

## Comunicación

- **HTTP:** lecturas PIR y heartbeat hacia Django (`/monitoring/readings/ingest/`).
- **MQTT:** comandos del backend en `siaac/zones/<zona>/commands`
  (`{"action":"BOTH","duration_seconds":15}`).
- **WiFi:** 2.4 GHz únicamente (el ESP32 no soporta 5 GHz).
