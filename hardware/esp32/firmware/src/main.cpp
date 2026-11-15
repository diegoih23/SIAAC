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
#if SIAAC_CAMERA_ENABLED
#include "esp_camera.h"
#endif

WiFiClient espClient;
PubSubClient mqtt(espClient);

unsigned long lastPirAt = 0;
unsigned long lastHeartbeatAt = 0;
bool pirReady = false;
bool sirenActive = false;

#if SIAAC_CAMERA_ENABLED
bool initializeCamera() {
  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer = LEDC_TIMER_0;
  config.pin_d0 = CAM_PIN_D0;
  config.pin_d1 = CAM_PIN_D1;
  config.pin_d2 = CAM_PIN_D2;
  config.pin_d3 = CAM_PIN_D3;
  config.pin_d4 = CAM_PIN_D4;
  config.pin_d5 = CAM_PIN_D5;
  config.pin_d6 = CAM_PIN_D6;
  config.pin_d7 = CAM_PIN_D7;
  config.pin_xclk = CAM_PIN_XCLK;
  config.pin_pclk = CAM_PIN_PCLK;
  config.pin_vsync = CAM_PIN_VSYNC;
  config.pin_href = CAM_PIN_HREF;
  config.pin_sccb_sda = CAM_PIN_SIOD;
  config.pin_sccb_scl = CAM_PIN_SIOC;
  config.pin_pwdn = CAM_PIN_PWDN;
  config.pin_reset = CAM_PIN_RESET;
  config.xclk_freq_hz = 20000000;
  config.pixel_format = PIXFORMAT_JPEG;
  config.frame_size = CAMERA_FRAME_SIZE;
  config.jpeg_quality = CAMERA_JPEG_QUALITY;
  config.fb_count = 1;
  config.grab_mode = CAMERA_GRAB_WHEN_EMPTY;
  return esp_camera_init(&config) == ESP_OK;
}

bool sendPhotoToBackend(camera_fb_t *frame) {
  if (WiFi.status() != WL_CONNECTED || !frame) return false;
  WiFiClient client;
  if (!client.connect(API_HOST, API_PORT)) return false;

  const String boundary = "----SIAACBoundary";
  const String path = String(API_BASE_PATH) + "/detection/events/ingest/";
  String prefix = "--" + boundary + "\r\n";
  prefix += "Content-Disposition: form-data; name=\"device_serial\"\r\n\r\n";
  prefix += DEVICE_SERIAL;
  prefix += "\r\n--" + boundary + "\r\n";
  prefix += "Content-Disposition: form-data; name=\"zone\"\r\n\r\n";
  prefix += String(ZONE_ID);
  prefix += "\r\n--" + boundary + "\r\n";
  prefix += "Content-Disposition: form-data; name=\"image\"; filename=\"esp32-capture.jpg\"\r\n";
  prefix += "Content-Type: image/jpeg\r\n\r\n";
  String suffix = "\r\n--" + boundary + "--\r\n";
  size_t contentLength = prefix.length() + frame->len + suffix.length();

  client.printf("POST %s HTTP/1.1\r\n", path.c_str());
  client.printf("Host: %s:%d\r\n", API_HOST, API_PORT);
  client.printf("X-Device-Key: %s\r\n", DEVICE_API_KEY);
  client.printf("Content-Type: multipart/form-data; boundary=%s\r\n", boundary.c_str());
  client.printf("Content-Length: %u\r\nConnection: close\r\n\r\n", (unsigned)contentLength);
  client.print(prefix);
  client.write(frame->buf, frame->len);
  client.print(suffix);

  unsigned long started = millis();
  while (client.connected() && !client.available() && millis() - started < 15000) delay(10);
  String status = client.readStringUntil('\n');
  client.stop();
  Serial.printf("[CAMERA] envío: %s", status.c_str());
  return status.indexOf(" 2") >= 0;
}

void captureAndSendPhoto() {
  camera_fb_t *frame = esp_camera_fb_get();
  if (!frame) {
    Serial.println("[CAMERA] no se pudo capturar");
    return;
  }
  sendPhotoToBackend(frame);
  esp_camera_fb_return(frame);
}
#endif

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

#if SIAAC_CAMERA_ENABLED
  if (!initializeCamera()) {
    Serial.println("[CAMERA] no disponible; se continuará sin cámara");
  }
#endif

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
#if SIAAC_CAMERA_ENABLED
      captureAndSendPhoto();
#endif
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
