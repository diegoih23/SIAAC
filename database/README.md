# Base de datos SIAAC (MariaDB)

## Archivos

| Archivo | Uso |
| --- | --- |
| `schema.sql` | DDL de referencia de todas las tablas, claves foráneas, índices y vistas. |
| `seed.sql` | Datos de ejemplo: cultivos, zonas, dispositivos, cámara, modelo YOLO y reglas. |
| `erd/siaac_erd.md` | Diagrama entidad-relación en Mermaid. |
| `migrations/README.md` | Ubicación de las migraciones reales (Django). |

> La fuente de verdad son las migraciones de Django. `schema.sql` usa
> `CREATE TABLE IF NOT EXISTS`, así que puede aplicarse después de `migrate`
> para revisar/crear lo que falte sin borrar datos.

## Crear la base de datos

```bash
mysql -u root -p < database/schema.sql
mysql -u root -p siaac_db < database/seed.sql
```

O con Docker (recomendado para desarrollo):

```bash
docker compose up -d mariadb
```

## Usuario de aplicación

```sql
CREATE USER IF NOT EXISTS 'siaac_user'@'%' IDENTIFIED BY 'siaac_password';
GRANT ALL PRIVILEGES ON siaac_db.* TO 'siaac_user'@'%';
FLUSH PRIVILEGES;
```

## Migraciones de Django

```bash
cd backend
python manage.py makemigrations users crops monitoring detection disuasion notifications reports
python manage.py migrate
python manage.py createsuperuser
```

## Relaciones principales

- `usuarios` 1—N `cultivos` (propietario) y `zonas` (responsable).
- `usuarios` 1—N `intentos_acceso` para auditoría de seguridad.
- `usuarios` 1—N `desafios_doble_factor` para autenticación 2FA.
- `usuarios` 1—N `codigos_verificacion_correo` para validar el correo durante el registro.
- `cultivos` 1—N `zonas`.
- `zonas` 1—N `dispositivos`, `camaras`, `lecturas_sensor`.
- `dispositivos` 1—N `eventos_deteccion`; `modelos_ia` 1—N `eventos_deteccion`.
- `eventos_deteccion` 1—N `activaciones_disuasion` y `notificaciones`.
- `zonas` 1—N `reglas_disuasion` y `reportes`.

## Respaldos

```bash
mysqldump -u siaac_user -p --single-transaction --routines --triggers siaac_db > respaldo_$(date +%F).sql
```
