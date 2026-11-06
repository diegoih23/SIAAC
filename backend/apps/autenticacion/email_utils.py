"""Plantillas de correo de autenticación de SIAAC."""
from html import escape

from django.conf import settings
from django.core.mail import EmailMultiAlternatives


def send_siaac_otp_email(*, recipient, subject, code, title, message, expires="10 minutos"):
    """Envía una versión HTML y otra de texto plano del correo OTP."""
    safe_title = escape(title)
    safe_message = escape(message)
    safe_recipient = escape(recipient)
    safe_code = escape(code)
    safe_expires = escape(expires)
    text_body = (
        f"SIAAC\n\n{title}\n\n{message}\n\n"
        f"Código de verificación: {code}\nVigencia: {expires}.\n\n"
        "Si no solicitaste este código, puedes ignorar este mensaje."
    )
    html_body = f"""
    <!doctype html><html lang="es"><body style="margin:0;background:#edf4ee;font-family:Arial,Helvetica,sans-serif;color:#24352b;">
      <div style="padding:32px 12px;"><div style="max-width:560px;margin:0 auto;background:#fff;border:1px solid #dce9df;border-radius:18px;overflow:hidden;box-shadow:0 8px 24px rgba(30,72,45,.10);">
        <div style="padding:24px 28px;background:#173d25;color:#fff;text-align:center;"><div style="font-size:28px;font-weight:800;letter-spacing:5px;">SIAAC</div><div style="margin-top:6px;color:#bde9c7;font-size:12px;letter-spacing:1px;">VIGILANCIA INTELIGENTE</div></div>
        <div style="padding:34px 30px;text-align:center;"><div style="display:inline-block;padding:8px 14px;border-radius:999px;background:#e7f6eb;color:#2d9759;font-size:12px;font-weight:700;letter-spacing:.7px;">VERIFICACIÓN DE SEGURIDAD</div>
          <h1 style="margin:20px 0 12px;color:#173d25;font-size:25px;">{safe_title}</h1><p style="margin:0 auto 24px;max-width:420px;color:#637568;font-size:15px;line-height:1.6;">{safe_message}</p>
          <div style="margin:0 auto 22px;padding:20px 12px;border:1px solid #bfe4c8;border-radius:14px;background:#f5fbf6;"><div style="margin-bottom:8px;color:#78907e;font-size:11px;letter-spacing:1.4px;text-transform:uppercase;">Tu código de verificación</div><div style="color:#20824a;font-size:38px;font-weight:800;letter-spacing:10px;line-height:1.2;">{safe_code}</div></div>
          <p style="margin:0;color:#788a7c;font-size:13px;">Este código es válido durante <strong>{safe_expires}</strong>.</p>
        </div>
        <div style="padding:18px 28px;background:#f6faf7;border-top:1px solid #e4eee6;text-align:center;color:#829387;font-size:12px;line-height:1.6;">Este mensaje fue enviado a {safe_recipient}.<br>Si no solicitaste este código, puedes ignorar este correo.<br><strong style="color:#2d9759;">SIAAC</strong> · Sistema Inteligente de Agricultura Asistida por Computadora</div>
      </div></div>
    </body></html>
    """
    email = EmailMultiAlternatives(
        subject=subject,
        body=text_body,
        from_email=getattr(settings, "DEFAULT_FROM_EMAIL", "seguridad@siaac.local"),
        to=[recipient],
    )
    email.attach_alternative(html_body, "text/html")
    email.send(fail_silently=True)
