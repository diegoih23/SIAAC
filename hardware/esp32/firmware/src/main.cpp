/**
 * SIAAC - Nodo ESP32
 * ---------------------------------------------------------------------------
 * Funciones:
 *   1. Lee el sensor PIR y reporta movimiento al backend Django.
 *   2. Publica/recibe comandos MQTT para activar la bocina y la luz.
 *   3. Envía un heartbeat periódico con su estado.
 *
 * Placa: ESP32 DevKit / WROOM-32. Ver docs/wiring.md para el conexionado.
 */
#include <Arduino.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include "config.h"

WiFiClient espClient;
PubSubClient mqtt(espClient);

unsigned long lastPirAt = 0;
unsigned long lastHeartbeatAt = 0;
bool pirReady = false;
bool sirenActive = false;

void setOutputs(bool sirenOn, bool lightOn) {
  digitalWrite(PIN_BUZZER, sirenOn ? HIGH : LOW);
  digitalWrite(PIN_LIGHT, lightOn ? HIGH : LOW);
}

void activateDisuasion(const String &action, unsigned long durationMs) {
  bool siren = (action == "SIREN" || action == "BOTH");
  bool light = (action == "LIGHT" || action == "BOTH");
  setOutputs(siren, light);
  sirenActive = siren || light;
  Serial.printf("[DISUASION] action=%s duration=%lums\n", action.c_str(), durationMs);
  delay(durationMs);              // el prototipo bloquea; usar Task si se requiere concurrencia
  setOutputs(false, false);
  sirenActive = false;
}

void onMqttMessage(char *topic, byte *payload, unsigned int length) {
  StaticJsonDocument<256> doc;
  DeserializationError error = deserializeJson(doc, payload, length);
  if (error) {
    Serial.println("[MQTT] JSON inválido");
    return;
  }
  const char *action = doc["action"] | "BOTH";
  unsigned long duration = doc["duration_seconds"] | 15;
  activateDisuasion(String(action), duration * 1000UL);
}

void ensureMqtt() {
  if (mqtt.connected()) {
    mqtt.loop();
    return;
  }
  Serial.print("[MQTT] conectando...");
  if (mqtt.connect(MQTT_CLIENT_ID)) {
    Serial.println(" OK");
    mqtt.subscribe(MQTT_TOPIC_CMD);
  } else {
    Serial.printf(" error=%d\n", mqtt.state());
    delay(3000);
  }
}

bool postJson(const String &path, const String &body) {
  if (WiFi.status() != WL_CONNECTED) return false;
  HTTPClient http;
  String url = String("http://") + API_HOST + ":" + API_PORT + API_BASE_PATH + path;
  http.begin(url);
  http.addHeader("Content-Type", "application/json");
  http.addHeader("X-Device-Key", DEVICE_API_KEY);
  int status = http.POST(body);
  if (status > 0) {
    Serial.printf("[HTTP] %s -> %d\n", path.c_str(), status);
  } else {
    Serial.printf("[HTTP] error: %s\n", http.errorToString(status).c_str());
  }
  http.end();
  return status >= 200 && status < 300;
}

void reportSensor(const char *type, float value, const char *unit) {
  StaticJsonDocument<256> doc;
  doc["zone"] = ZONE_ID;
  doc["sensor_type"] = type;
  doc["value"] = value;
  doc["unit"] = unit;
  char body[256];
  serializeJson(doc, body);
  postJson("/monitoring/readings/ingest/", body);
}

void sendHeartbeat() {
  StaticJsonDocument<256> doc;
  doc["ip_address"] = WiFi.localIP().toString();
  doc["firmware_version"] = "1.0.0";
  doc["status"] = "ONLINE";
  char body[256];
  serializeJson(doc, body);

  StaticJsonDocument<128> mqttDoc;
  mqttDoc["serial"] = DEVICE_SERIAL;
  mqttDoc["ip"] = WiFi.localIP().toString();
  mqttDoc["uptime_s"] = millis() / 1000;
  char mqttBody[128];
  serializeJson(mqttDoc, mqttBody);
  mqtt.publish(MQTT_TOPIC_HB, mqttBody);

  // El endpoint real de heartbeat requiere el id del dispositivo; se usa
  // el número 1 como ejemplo del prototipo.
  postJson("/detection/devices/1/heartbeat/", body);
}

void setup() {
  Serial.begin(115200);
  pinMode(PIN_PIR, INPUT);
  pinMode(PIN_BUZZER, OUTPUT);
  pinMode(PIN_LIGHT, OUTPUT);
  pinMode(PIN_LED_STATUS, OUTPUT);
  setOutputs(false, false);

  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  Serial.print("[WiFi] conectando");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.printf("\n[WiFi] IP: %s\n", WiFi.localIP().toString().c_str());

  mqtt.setServer(MQTT_HOST, MQTT_PORT);
  mqtt.setCallback(onMqttMessage);
  mqtt.setBufferSize(512);

  Serial.printf("[PIR] calibrando %lu ms...\n", PIR_WARMUP_MS);
  delay(PIR_WARMUP_MS);
  pirReady = true;
  digitalWrite(PIN_LED_STATUS, HIGH);
}

void loop() {
  ensureMqtt();

  if (pirReady) {
    bool motion = digitalRead(PIN_PIR) == HIGH;
    if (motion && millis() - lastPirAt > PIR_COOLDOWN_MS) {
      lastPirAt = millis();
      Serial.println("[PIR] Movimiento detectado");
      reportSensor("PIR", 1, "bool");
    } else if (!motion && millis() - lastPirAt > PIR_COOLDOWN_MS) {
      // Reporte de ausencia de movimiento una vez por ventana.
      reportSensor("PIR", 0, "bool");
    }
  }

  if (millis() - lastHeartbeatAt > HEARTBEAT_MS) {
    lastHeartbeatAt = millis();
    sendHeartbeat();
  }

  delay(250);
}
