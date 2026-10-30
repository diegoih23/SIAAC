# Migraciones

Las migraciones reales viven junto a cada app de Django:

```
backend/apps/autenticacion/migrations/
backend/apps/cultivos/migrations/
backend/apps/monitoreo/migrations/
backend/apps/reportes/migrations/
backend/apps/respuestas/migrations/
backend/apps/notificaciones/migrations/
backend/apps/deteccion/migrations/
```

Generarlas y aplicarlas:

```bash
cd backend
python manage.py makemigrations
python manage.py migrate
```

Este directorio queda reservado para migraciones SQL manuales o scripts de
mantenimiento (por ejemplo, índices adicionales o ajustes de producción).
