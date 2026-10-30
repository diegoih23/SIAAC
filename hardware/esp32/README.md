# ESP32 - Nodo de sensores y actuadores

## Requisitos

- [PlatformIO Core](https://platformio.org/install) o la extensión de PlatformIO
  para VS Code.
- ESP32 DevKit V1 (o compatible).
- Driver USB CP210x/CH340 según la placa.

## Configuración

```bash
cd firmware
cp include/config.example.h include/config.h
# Editar config.h: WiFi, IP del backend, serial, API key, zona y pines
```

> `config.h` contiene credenciales y está excluido de Git.

## Compilar y cargar

```bash
pio run                 # compila
pio run --target upload # carga por USB
pio device monitor      # monitor serial 115200
```

## Comportamiento

1. Conecta a WiFi y al broker MQTT.
2. Calibra el PIR durante 30 s.
3. Reporta movimiento a `/api/v1/monitoring/readings/ingest/`.
4. Envía heartbeat cada 60 s.
5. Escucha `siaac/zones/<zona>/commands` y activa sirena/luces.

## Estructura

```
firmware/
├── platformio.ini
├── include/config.example.h
└── src/main.cpp
```

Ver `docs/wiring.md` para pines, relés y alimentación.
