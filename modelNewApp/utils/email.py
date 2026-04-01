import os
from django.conf import settings

# Solo importa SendGrid si hay API Key
if settings.SENDGRID_API_KEY:
    from sendgrid import SendGridAPIClient
    from sendgrid.helpers.mail import Mail

from django.core.mail import send_mail as django_send_mail

def enviar_correo(destino, asunto, contenido_html):
    """
    Envía correo.
    - Si SENDGRID_API_KEY existe -> usa SendGrid (PythonAnywhere)
    - Si no -> usa send_mail de Django (SMTP local)
    """
    if settings.SENDGRID_API_KEY:
        message = Mail(
            from_email='no-reply@sistema.com',  # remitente verificado
            to_emails=destino,
            subject=asunto,
            html_content=contenido_html
        )
        try:
            sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
            response = sg.send(message)
            return response.status_code
        except Exception as e:
            print("Error enviando correo con SendGrid:", e)
            return None
    else:
        # Local: Django SMTP
        django_send_mail(
            asunto,
            '',  # contenido de texto vacío, solo HTML
            settings.DEFAULT_FROM_EMAIL,
            [destino],
            html_message=contenido_html,
            fail_silently=False,
        )
        return 200