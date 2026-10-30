-- =============================================================================
-- SIAAC - Esquema de base de datos MariaDB
-- Sistema Inteligente de Agricultura Asistida por Computadora
--
-- IMPORTANTE:
--   * La fuente de verdad del esquema son las migraciones de Django
--     (python manage.py makemigrations && python manage.py migrate).
--   * Este archivo documenta el modelo físico y usa CREATE TABLE IF NOT EXISTS,
--     por lo que puede aplicarse después de migrar sin destruir información.
--   * Motor recomendado: MariaDB 10.6+ / 11.x, charset utf8mb4.
-- =============================================================================

CREATE DATABASE IF NOT EXISTS siaac_db
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE siaac_db;

-- -----------------------------------------------------------------------------
-- MÓDULO 1: AUTENTICACIÓN Y SESIÓN DE USUARIOS
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS usuarios (
  id              BIGINT AUTO_INCREMENT PRIMARY KEY,
  password        VARCHAR(128) NOT NULL,
  last_login      DATETIME(6) NULL,
  is_superuser    TINYINT(1) NOT NULL DEFAULT 0,
  username        VARCHAR(150) NOT NULL,
  first_name      VARCHAR(150) NOT NULL DEFAULT '',
  last_name       VARCHAR(150) NOT NULL DEFAULT '',
  email           VARCHAR(254) NOT NULL DEFAULT '',
  is_staff        TINYINT(1) NOT NULL DEFAULT 0,
  is_active       TINYINT(1) NOT NULL DEFAULT 1,
  date_joined     DATETIME(6) NOT NULL,
  role            VARCHAR(20) NOT NULL DEFAULT 'VIEWER',
  phone           VARCHAR(20) NOT NULL DEFAULT '',
  avatar          VARCHAR(100) NULL,
  is_email_verified TINYINT(1) NOT NULL DEFAULT 0,
  last_login_ip   CHAR(39) NULL,
  UNIQUE KEY uniq_users_username (username),
  KEY idx_users_role (role),
  KEY idx_users_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS sesiones_usuario (
  id            BIGINT AUTO_INCREMENT PRIMARY KEY,
  created_at    DATETIME(6) NOT NULL,
  updated_at    DATETIME(6) NOT NULL,
  user_id       BIGINT NOT NULL,
  refresh_jti   VARCHAR(64) NOT NULL DEFAULT '',
  ip_address    CHAR(39) NULL,
  user_agent    VARCHAR(300) NOT NULL DEFAULT '',
  device_label  VARCHAR(120) NOT NULL DEFAULT '',
  login_at      DATETIME(6) NOT NULL,
  logout_at     DATETIME(6) NULL,
  is_active     TINYINT(1) NOT NULL DEFAULT 1,
  KEY idx_session_user (user_id),
  KEY idx_session_jti (refresh_jti),
  KEY idx_session_active (is_active),
  CONSTRAINT fk_session_user FOREIGN KEY (user_id) REFERENCES usuarios (id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- MÓDULO 2: GESTIÓN DE CULTIVOS Y ZONAS
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS cultivos (
  id               BIGINT AUTO_INCREMENT PRIMARY KEY,
  created_at       DATETIME(6) NOT NULL,
  updated_at       DATETIME(6) NOT NULL,
  name             VARCHAR(120) NOT NULL,
  scientific_name  VARCHAR(160) NOT NULL DEFAULT '',
  variety          VARCHAR(120) NOT NULL DEFAULT '',
  description      LONGTEXT NOT NULL,
  planting_date    DATE NULL,
  harvest_date     DATE NULL,
  status           VARCHAR(20) NOT NULL DEFAULT 'GROWING',
  owner_id         BIGINT NULL,
  KEY idx_crop_name (name),
  KEY idx_crop_status (status),
  CONSTRAINT fk_crop_owner FOREIGN KEY (owner_id) REFERENCES usuarios (id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS zonas (
  id             BIGINT AUTO_INCREMENT PRIMARY KEY,
  created_at     DATETIME(6) NOT NULL,
  updated_at     DATETIME(6) NOT NULL,
  is_deleted     TINYINT(1) NOT NULL DEFAULT 0,
  deleted_at     DATETIME(6) NULL,
  name           VARCHAR(120) NOT NULL,
  code           VARCHAR(40) NOT NULL,
  crop_id        BIGINT NULL,
  description    LONGTEXT NOT NULL,
  latitude       DECIMAL(9,6) NULL,
  longitude      DECIMAL(9,6) NULL,
  area_m2        DECIMAL(10,2) NULL,
  responsible_id BIGINT NULL,
  is_active      TINYINT(1) NOT NULL DEFAULT 1,
  UNIQUE KEY uniq_zone_code (code),
  KEY idx_zone_name (name),
  KEY idx_zone_active (is_active),
  CONSTRAINT fk_zone_crop FOREIGN KEY (crop_id) REFERENCES cultivos (id) ON DELETE SET NULL,
  CONSTRAINT fk_zone_responsible FOREIGN KEY (responsible_id) REFERENCES usuarios (id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- DETECCIÓN AUTOMÁTICA: HARDWARE (ESP32 / RASPBERRY PI / CÁMARAS)
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS dispositivos (
  id               BIGINT AUTO_INCREMENT PRIMARY KEY,
  created_at       DATETIME(6) NOT NULL,
  updated_at       DATETIME(6) NOT NULL,
  name             VARCHAR(120) NOT NULL,
  device_type      VARCHAR(10) NOT NULL,
  serial_number    VARCHAR(80) NOT NULL,
  zone_id          BIGINT NULL,
  ip_address       CHAR(39) NULL,
  api_key          VARCHAR(64) NOT NULL,
  firmware_version VARCHAR(40) NOT NULL DEFAULT '',
  status           VARCHAR(20) NOT NULL DEFAULT 'OFFLINE',
  last_seen        DATETIME(6) NULL,
  metadata         JSON NOT NULL,
  UNIQUE KEY uniq_device_serial (serial_number),
  UNIQUE KEY uniq_device_api_key (api_key),
  KEY idx_device_zone (zone_id),
  KEY idx_device_status (status),
  CONSTRAINT fk_device_zone FOREIGN KEY (zone_id) REFERENCES zonas (id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- MÓDULO 3: MONITOREO EN TIEMPO REAL
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS camaras (
  id               BIGINT AUTO_INCREMENT PRIMARY KEY,
  created_at       DATETIME(6) NOT NULL,
  updated_at       DATETIME(6) NOT NULL,
  zone_id          BIGINT NOT NULL,
  name             VARCHAR(120) NOT NULL,
  stream_url       VARCHAR(500) NOT NULL,
  has_night_vision TINYINT(1) NOT NULL DEFAULT 1,
  status           VARCHAR(20) NOT NULL DEFAULT 'OFFLINE',
  last_frame_at    DATETIME(6) NULL,
  KEY idx_camera_zone (zone_id),
  CONSTRAINT fk_camera_zone FOREIGN KEY (zone_id) REFERENCES zonas (id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS lecturas_sensor (
  id           BIGINT AUTO_INCREMENT PRIMARY KEY,
  created_at   DATETIME(6) NOT NULL,
  updated_at   DATETIME(6) NOT NULL,
  zone_id      BIGINT NOT NULL,
  device_id    BIGINT NULL,
  sensor_type  VARCHAR(10) NOT NULL,
  value        DOUBLE NOT NULL,
  unit         VARCHAR(20) NOT NULL DEFAULT '',
  recorded_at  DATETIME(6) NOT NULL,
  raw_payload  JSON NOT NULL,
  KEY idx_reading_zone_type_date (zone_id, sensor_type, recorded_at DESC),
  KEY idx_reading_recorded (recorded_at),
  CONSTRAINT fk_reading_zone FOREIGN KEY (zone_id) REFERENCES zonas (id) ON DELETE CASCADE,
  CONSTRAINT fk_reading_device FOREIGN KEY (device_id) REFERENCES dispositivos (id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- DETECCIÓN AUTOMÁTICA: MODELO YOLO Y EVENTOS
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS modelos_ia (
  id                   BIGINT AUTO_INCREMENT PRIMARY KEY,
  created_at           DATETIME(6) NOT NULL,
  updated_at           DATETIME(6) NOT NULL,
  name                 VARCHAR(120) NOT NULL,
  version              VARCHAR(40) NOT NULL,
  architecture         VARCHAR(40) NOT NULL DEFAULT 'YOLO11',
  weights_path         VARCHAR(500) NOT NULL,
  confidence_threshold DOUBLE NOT NULL DEFAULT 0.45,
  iou_threshold        DOUBLE NOT NULL DEFAULT 0.50,
  classes              JSON NOT NULL,
  is_active            TINYINT(1) NOT NULL DEFAULT 0,
  UNIQUE KEY uniq_model_version (name, version),
  KEY idx_model_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS eventos_deteccion (
  id                   BIGINT AUTO_INCREMENT PRIMARY KEY,
  created_at           DATETIME(6) NOT NULL,
  updated_at           DATETIME(6) NOT NULL,
  zone_id              BIGINT NOT NULL,
  device_id            BIGINT NULL,
  camera_id            BIGINT NULL,
  ai_model_id          BIGINT NULL,
  object_class         VARCHAR(80) NOT NULL,
  confidence           DOUBLE NOT NULL,
  bbox                 JSON NOT NULL,
  image                VARCHAR(100) NULL,
  detected_at          DATETIME(6) NOT NULL,
  status               VARCHAR(20) NOT NULL DEFAULT 'NEW',
  reviewed_by_id       BIGINT NULL,
  reviewed_at          DATETIME(6) NULL,
  notes                LONGTEXT NOT NULL,
  disuasion_triggered  TINYINT(1) NOT NULL DEFAULT 0,
  KEY idx_event_zone_date (zone_id, detected_at DESC),
  KEY idx_event_class_date (object_class, detected_at DESC),
  KEY idx_event_status (status),
  CONSTRAINT fk_event_zone FOREIGN KEY (zone_id) REFERENCES zonas (id) ON DELETE CASCADE,
  CONSTRAINT fk_event_device FOREIGN KEY (device_id) REFERENCES dispositivos (id) ON DELETE SET NULL,
  CONSTRAINT fk_event_camera FOREIGN KEY (camera_id) REFERENCES camaras (id) ON DELETE SET NULL,
  CONSTRAINT fk_event_model FOREIGN KEY (ai_model_id) REFERENCES modelos_ia (id) ON DELETE SET NULL,
  CONSTRAINT fk_event_reviewer FOREIGN KEY (reviewed_by_id) REFERENCES usuarios (id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- MÓDULO 5: CONFIGURACIÓN Y RESPUESTA DISUASIVA
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS reglas_disuasion (
  id               BIGINT AUTO_INCREMENT PRIMARY KEY,
  created_at       DATETIME(6) NOT NULL,
  updated_at       DATETIME(6) NOT NULL,
  name             VARCHAR(120) NOT NULL,
  zone_id          BIGINT NOT NULL,
  trigger_classes  JSON NOT NULL,
  min_confidence   DOUBLE NOT NULL DEFAULT 0.60,
  start_time       TIME(6) NULL,
  end_time         TIME(6) NULL,
  action           VARCHAR(10) NOT NULL DEFAULT 'BOTH',
  duration_seconds INT UNSIGNED NOT NULL DEFAULT 15,
  is_active        TINYINT(1) NOT NULL DEFAULT 1,
  created_by_id    BIGINT NULL,
  KEY idx_rule_zone (zone_id),
  KEY idx_rule_active (is_active),
  CONSTRAINT fk_rule_zone FOREIGN KEY (zone_id) REFERENCES zonas (id) ON DELETE CASCADE,
  CONSTRAINT fk_rule_creator FOREIGN KEY (created_by_id) REFERENCES usuarios (id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS activaciones_disuasion (
  id              BIGINT AUTO_INCREMENT PRIMARY KEY,
  created_at      DATETIME(6) NOT NULL,
  updated_at      DATETIME(6) NOT NULL,
  rule_id         BIGINT NULL,
  event_id        BIGINT NULL,
  device_id       BIGINT NULL,
  command         JSON NOT NULL,
  status          VARCHAR(20) NOT NULL DEFAULT 'PENDING',
  response        LONGTEXT NOT NULL,
  started_at      DATETIME(6) NOT NULL,
  ended_at        DATETIME(6) NULL,
  triggered_by_id BIGINT NULL,
  KEY idx_activation_rule (rule_id),
  KEY idx_activation_event (event_id),
  KEY idx_activation_status (status),
  CONSTRAINT fk_activation_rule FOREIGN KEY (rule_id) REFERENCES reglas_disuasion (id) ON DELETE SET NULL,
  CONSTRAINT fk_activation_event FOREIGN KEY (event_id) REFERENCES eventos_deteccion (id) ON DELETE SET NULL,
  CONSTRAINT fk_activation_device FOREIGN KEY (device_id) REFERENCES dispositivos (id) ON DELETE SET NULL,
  CONSTRAINT fk_activation_user FOREIGN KEY (triggered_by_id) REFERENCES usuarios (id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- MÓDULO 6: GESTIÓN DE NOTIFICACIONES
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS notificaciones (
  id               BIGINT AUTO_INCREMENT PRIMARY KEY,
  created_at       DATETIME(6) NOT NULL,
  updated_at       DATETIME(6) NOT NULL,
  user_id          BIGINT NOT NULL,
  title            VARCHAR(160) NOT NULL,
  message          LONGTEXT NOT NULL,
  channel          VARCHAR(10) NOT NULL DEFAULT 'IN_APP',
  category         VARCHAR(20) NOT NULL DEFAULT 'SYSTEM',
  priority         VARCHAR(10) NOT NULL DEFAULT 'NORMAL',
  is_read          TINYINT(1) NOT NULL DEFAULT 0,
  read_at          DATETIME(6) NULL,
  sent_at          DATETIME(6) NULL,
  payload          JSON NOT NULL,
  related_event_id BIGINT NULL,
  KEY idx_notification_user_read_date (user_id, is_read, created_at DESC),
  KEY idx_notification_category (category),
  CONSTRAINT fk_notification_user FOREIGN KEY (user_id) REFERENCES usuarios (id) ON DELETE CASCADE,
  CONSTRAINT fk_notification_event FOREIGN KEY (related_event_id) REFERENCES eventos_deteccion (id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS preferencias_notificacion (
  id                BIGINT AUTO_INCREMENT PRIMARY KEY,
  created_at        DATETIME(6) NOT NULL,
  updated_at        DATETIME(6) NOT NULL,
  user_id           BIGINT NOT NULL,
  category          VARCHAR(20) NOT NULL,
  channel           VARCHAR(10) NOT NULL,
  enabled           TINYINT(1) NOT NULL DEFAULT 1,
  quiet_hours_start TIME(6) NULL,
  quiet_hours_end   TIME(6) NULL,
  UNIQUE KEY uniq_user_category_channel (user_id, category, channel),
  CONSTRAINT fk_preference_user FOREIGN KEY (user_id) REFERENCES usuarios (id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- MÓDULO 4: SUPERVISIÓN Y REPORTES
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS reportes (
  id              BIGINT AUTO_INCREMENT PRIMARY KEY,
  created_at      DATETIME(6) NOT NULL,
  updated_at      DATETIME(6) NOT NULL,
  title           VARCHAR(160) NOT NULL,
  report_type     VARCHAR(20) NOT NULL DEFAULT 'GENERAL',
  format          VARCHAR(5) NOT NULL DEFAULT 'PDF',
  zone_id         BIGINT NULL,
  period_start    DATETIME(6) NOT NULL,
  period_end      DATETIME(6) NOT NULL,
  parameters      JSON NOT NULL,
  status          VARCHAR(20) NOT NULL DEFAULT 'PENDING',
  file            VARCHAR(100) NULL,
  error_message   LONGTEXT NOT NULL,
  generated_by_id BIGINT NULL,
  KEY idx_report_type (report_type),
  KEY idx_report_zone (zone_id),
  KEY idx_report_created (created_at),
  CONSTRAINT fk_report_zone FOREIGN KEY (zone_id) REFERENCES zonas (id) ON DELETE SET NULL,
  CONSTRAINT fk_report_user FOREIGN KEY (generated_by_id) REFERENCES usuarios (id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- VISTAS DE APOYO PARA TABLEROS Y REPORTES
-- -----------------------------------------------------------------------------
CREATE OR REPLACE VIEW vw_detecciones_por_zona AS
SELECT z.id AS zone_id,
       z.code,
       z.name AS zone_name,
       e.object_class,
       COUNT(*) AS total,
       ROUND(AVG(e.confidence), 3) AS confidence_avg,
       MAX(e.detected_at) AS last_detection
FROM eventos_deteccion e
JOIN zonas z ON z.id = e.zone_id
GROUP BY z.id, z.code, z.name, e.object_class;

CREATE OR REPLACE VIEW vw_estado_dispositivos AS
SELECT d.id,
       d.name,
       d.device_type,
       d.serial_number,
       d.status,
       d.last_seen,
       z.code AS zone_code,
       z.name AS zone_name
FROM dispositivos d
LEFT JOIN zonas z ON z.id = d.zone_id;
