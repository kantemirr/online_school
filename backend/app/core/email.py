"""Отправка email через SMTP (в dev — MailHog).

Используется воркером (фоновая задача send_email). Текст писем — простой
HTML; в dev всё уходит в MailHog и видно на http://localhost:8025.
"""
import aiosmtplib
from email.message import EmailMessage

from app.core.config import get_settings
from app.core.logging import get_logger

_settings = get_settings()
logger = get_logger(__name__)


async def send_email_smtp(to: str, subject: str, html: str) -> None:
    message = EmailMessage()
    message["From"] = _settings.EMAIL_FROM
    message["To"] = to
    message["Subject"] = subject
    message.set_content("Для просмотра письма используйте HTML-клиент.")
    message.add_alternative(html, subtype="html")

    await aiosmtplib.send(
        message,
        hostname=_settings.SMTP_HOST,
        port=_settings.SMTP_PORT,
        start_tls=False,
    )
    logger.info("email sent to %s: %s", to, subject)


def verification_email(link: str) -> tuple[str, str]:
    subject = "Подтверждение регистрации в CodeKids"
    html = (
        "<h2>Добро пожаловать в CodeKids!</h2>"
        "<p>Чтобы активировать аккаунт, перейдите по ссылке:</p>"
        f'<p><a href="{link}">{link}</a></p>'
        "<p>Ссылка действительна 24 часа.</p>"
    )
    return subject, html


def password_reset_email(link: str) -> tuple[str, str]:
    subject = "Сброс пароля в CodeKids"
    html = (
        "<h2>Сброс пароля</h2>"
        "<p>Вы запросили сброс пароля. Перейдите по ссылке:</p>"
        f'<p><a href="{link}">{link}</a></p>'
        "<p>Ссылка действительна 1 час. Если вы не запрашивали сброс — проигнорируйте письмо.</p>"
    )
    return subject, html
