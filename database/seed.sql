-- =============================================================================
-- SIAAC - Datos de ejemplo (ejecutar después de las migraciones de Django)
-- Las contraseñas se crean con: python manage.py createsuperuser
-- =============================================================================
USE siaac_db;

INSERT IGNORE INTO cultivos
  (id, created_at, updated_at, name, scientific_name, variety, description, status, planting_date)
VALUES
  (1, NOW(6), NOW(6), 'Maíz', 'Zea mays', 'Amarillo criollo', 'Lote experimental de maíz', 'GROWING', CURDATE()),
  (2, NOW(6), NOW(6), 'Tomate', 'Solanum lycopersicum', 'Chonto', 'Cultivo bajo invernadero', 'GROWING', CURDATE());

INSERT IGNORE INTO zonas
  (id, created_at, updated_at, is_deleted, name, code, crop_id, description, latitude, longitude, area_m2, is_active)
VALUES
  (1, NOW(6), NOW(6), 0, 'Lote norte', 'Z-01', 1, 'Zona perimetral con cámara nocturna', 4.711000, -74.072100, 1200.00, 1),
  (2, NOW(6), NOW(6), 0, 'Invernadero', 'Z-02', 2, 'Zona techada con sensor de humedad', 4.711500, -74.072500, 350.00, 1);

INSERT IGNORE INTO dispositivos
  (id, created_at, updated_at, name, device_type, serial_number, zone_id, ip_address, api_key, firmware_version, status, metadata)
VALUES
  (1, NOW(6), NOW(6), 'ESP32 Lote norte', 'ESP32', 'ESP32-SIAAC-001', 1, '192.168.1.50',
   'demo-api-key-esp32-001', '1.0.0', 'ONLINE', JSON_OBJECT('pir_pin', 27, 'siren_pin', 26)),
  (2, NOW(6), NOW(6), 'Raspberry Pi 4', 'RPI', 'RPI-SIAAC-001', 1, '192.168.1.60',
   'demo-api-key-rpi-001', '1.0.0', 'ONLINE', JSON_OBJECT('camera', 'IR-CUT 1080p', 'yolo', 'yolo11n')),
  (3, NOW(6), NOW(6), 'ESP32 Invernadero', 'ESP32', 'ESP32-SIAAC-002', 2, '192.168.1.51',
   'demo-api-key-esp32-002', '1.0.0', 'OFFLINE', JSON_OBJECT('sensor', 'DHT22'));

INSERT IGNORE INTO camaras
  (id, created_at, updated_at, zone_id, name, stream_url, has_night_vision, status)
VALUES
  (1, NOW(6), NOW(6), 1, 'Cámara perimetral IR', 'rtsp://192.168.1.60:8554/norte', 1, 'ONLINE'),
  (2, NOW(6), NOW(6), 2, 'Cámara invernadero', 'rtsp://192.168.1.61:8554/invernadero', 1, 'OFFLINE');

INSERT IGNORE INTO modelos_ia
  (id, created_at, updated_at, name, version, architecture, weights_path, confidence_threshold, iou_threshold, classes, is_active)
VALUES
  (1, NOW(6), NOW(6), 'SIAAC Intrusos', '1.0', 'YOLO11', 'ml/yolo/weights/siaac_intrusos.pt', 0.45, 0.50,
   JSON_ARRAY('person', 'dog', 'cat', 'bird', 'car', 'motorcycle'), 1);

INSERT IGNORE INTO reglas_disuasion
  (id, created_at, updated_at, name, zone_id, trigger_classes, min_confidence, action, duration_seconds, is_active)
VALUES
  (1, NOW(6), NOW(6), 'Intrusión nocturna', 1, JSON_ARRAY('person'), 0.65, 'BOTH', 15, 1),
  (2, NOW(6), NOW(6), 'Animales en el lote', 1, JSON_ARRAY('dog', 'cat', 'bird'), 0.70, 'SIREN', 10, 1);

-- Lecturas de ejemplo (PIR + temperatura)
INSERT INTO lecturas_sensor
  (created_at, updated_at, zone_id, device_id, sensor_type, value, unit, recorded_at, raw_payload)
VALUES
  (NOW(6), NOW(6), 1, 1, 'PIR', 0, 'bool', NOW(6), JSON_OBJECT('source', 'seed')),
  (NOW(6), NOW(6), 1, 1, 'TEMP', 24.6, 'C', NOW(6), JSON_OBJECT('source', 'seed')),
  (NOW(6), NOW(6), 2, 3, 'SOIL', 42.0, '%', NOW(6), JSON_OBJECT('source', 'seed'));

-- Nota: los usuarios se crean con el comando de Django:
--   python manage.py createsuperuser
-- y luego se les asigna role = 'ADMIN' desde el admin o con:
--   UPDATE usuarios SET role = 'ADMIN' WHERE username = 'admin';
