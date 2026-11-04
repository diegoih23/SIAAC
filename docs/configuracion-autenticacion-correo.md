# Configuración de autenticación y correo SIAAC

## Error de conexión del frontend

Si Vite muestra:

```text
ECONNREFUSED 127.0.0.1:8000
```

significa que el backend de Django no está ejecutándose. Iniciarlo con:

```bash
cd /home/juan/Procesos_SFTW/SIAAC/SIAAC/backend
source .venv/bin/activate
python manage.py runserver 0.0.0.0:8000
```

El backend debe permanecer activo en una terminal separada.

## Configuración SMTP

Editar el archivo:

```text
backend/.env
```

Para Gmail:

```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_USE_SSL=False
EMAIL_HOST_USER=tu-cuenta@gmail.com
EMAIL_HOST_PASSWORD=tu-contraseña-de-aplicación
DEFAULT_FROM_EMAIL=tu-cuenta@gmail.com
```

`EMAIL_HOST_PASSWORD` debe ser una **contraseña de aplicación** de Google, no la contraseña normal de la cuenta. Debe escribirse sin espacios.

La cuenta debe tener habilitada la verificación en dos pasos para poder generar una contraseña de aplicación.

## Inicio del frontend

En otra terminal:

```bash
cd /home/juan/Procesos_SFTW/SIAAC/SIAAC/frontend
npm run dev
```

Abrir:

```text
http://10.20.137.123:5173/login
```

## Flujo de registro

1. Seleccionar **Regístrate**.
2. Completar nombre, apellido, correo, celular opcional, usuario opcional y contraseña.
3. SIAAC crea la cuenta como no verificada.
4. Se envía un código OTP de seis dígitos al correo.
5. Introducir el código en la pantalla **Confirma tu correo**.
6. Después de verificarlo, el usuario puede iniciar sesión.

El código vence en 10 minutos y permite hasta cinco intentos.

## Desarrollo sin SMTP

Si no se configura SMTP, los códigos se muestran en la terminal donde corre Django usando:

```env
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

## Reiniciar después de cambiar `.env`

Es necesario detener y volver a iniciar Django después de modificar el archivo `.env`:

```bash
Ctrl+C
python manage.py runserver 0.0.0.0:8000
```

Nunca guardar contraseñas reales ni contraseñas de aplicación dentro de archivos versionados.
