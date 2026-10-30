// Copiar este archivo como config.h y ajustar los valores del prototipo.
#pragma once

// ------------------------- Red -------------------------
#define WIFI_SSID       "NOMBRE_DE_LA_RED"
#define WIFI_PASSWORD   "CLAVE_WIFI"

// ---------------------- Backend SIAAC ------------------
// IP de la computadora que ejecuta Django (no usar localhost en el ESP32)
#define API_HOST        "192.168.1.100"
#define API_PORT        8000
#define API_BASE_PATH   "/api/v1"
#define DEVICE_SERIAL   "ESP32-SIAAC-001"
#define DEVICE_API_KEY  "demo-api-key-esp32-001"
#define ZONE_ID         1

// ------------------------- MQTT ------------------------
#define MQTT_HOST       "192.168.1.100"
#define MQTT_PORT       1883
#define MQTT_CLIENT_ID  "siaac-esp32-001"
#define MQTT_TOPIC_CMD  "siaac/zones/1/commands"
#define MQTT_TOPIC_HB   "siaac/zones/1/heartbeat"

// ------------------------- Pines -----------------------
#define PIN_PIR         27   // Sensor de movimiento PIR
#define PIN_BUZZER      26   // Bocina / sirena
#define PIN_LIGHT       25   // Luz disuasiva o relé
#define PIN_LED_STATUS  2    // LED integrado de la placa

// ---------------------- Comportamiento -----------------
#define PIR_WARMUP_MS       30000UL  // Calibración del PIR al iniciar
#define PIR_COOLDOWN_MS     8000UL   // Evita lecturas duplicadas
#define HEARTBEAT_MS        60000UL  // Latido hacia el backend
#define DEFAULT_SIREN_MS    15000UL  // Duración por defecto de la sirena
