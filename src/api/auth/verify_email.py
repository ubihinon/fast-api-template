from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from pydantic import EmailStr

mail_config = ConnectionConfig(
    MAIL_USERNAME="your_email@gmail.com",
    MAIL_PASSWORD="your_app_password",
    MAIL_FROM="noreply@yourdomain.com",
    MAIL_PORT=587,
    MAIL_SERVER="smtp.gmail.com",
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
)

fastmail = FastMail(mail_config)


async def send_magic_link(email: EmailStr, token: str, user_id: str):
    """Отправляет Magic Link на email."""
    magic_link = f"http://localhost:8000/auth/verify?token={token}&user_id={user_id}"

    html = f"""
    <h2>Вход в систему</h2>
    <p>Для входа нажмите на кнопку ниже:</p>
    <a href="{magic_link}" style="background-color: #4CAF50; color: white; padding: 10px 20px; text-decoration: none; border-radius: 4px; display: inline-block;">
        Войти без пароля
    </a>
    <p>Ссылка действительна 10 минут.</p>
    """

    message = MessageSchema(
        subject="Ваша ссылка для входа",
        recipients=[email],
        body=html,
        subtype=MessageType.html,
    )

    await fastmail.send_message(message)
