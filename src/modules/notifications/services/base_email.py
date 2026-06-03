import logging
from typing import Optional

from fastapi import BackgroundTasks
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from fastapi_mail.errors import ConnectionErrors

from modules.notifications.schemas.email_payload import EmailPayload
from modules.notifications.settings import EmailSettings

logger = logging.getLogger("email_service")


class BaseEmailService:
    """
    Базовый класс email-сервиса, инкапсулирующий работу с fastapi_mail.
    Предоставляет методы для синхронной, асинхронной и фоновой отправки писем,
    а также поддержку HTML-шаблонов Jinja2.
    """

    def __init__(self, settings: EmailSettings):
        self.settings = settings
        self.config = self._get_connection_config()
        self.fastmail = FastMail(self.config)

    def _get_connection_config(self) -> ConnectionConfig:
        return ConnectionConfig(
            MAIL_USERNAME=self.settings.MAIL_USERNAME,
            MAIL_PASSWORD=self.settings.MAIL_PASSWORD,
            MAIL_FROM=self.settings.MAIL_FROM,
            MAIL_PORT=self.settings.MAIL_PORT,
            MAIL_SERVER=self.settings.MAIL_SERVER,
            MAIL_FROM_NAME=self.settings.MAIL_FROM_NAME,
            MAIL_STARTTLS=self.settings.MAIL_STARTTLS,
            MAIL_SSL_TLS=self.settings.MAIL_SSL_TLS,
            USE_CREDENTIALS=self.settings.USE_CREDENTIALS,
            VALIDATE_CERTS=self.settings.VALIDATE_CERTS,
            TEMPLATE_FOLDER=self.settings.TEMPLATE_FOLDER,
            SUPPRESS_SEND=self.settings.SUPPRESS_SEND
        )

    def _prepare_message(
        self,
        payload: EmailPayload,
        template_name: Optional[str] = None,
        subtype: MessageType = MessageType.html
    ) -> MessageSchema:
        # Если используется шаблон, тело письма передается как контекст Jinja2 (словарь)
        body = payload.body
        if template_name and not isinstance(body, dict):
            logger.warning("При использовании шаблона 'body' должен быть словарем (контекстом шаблона).")
            body = {}

        return MessageSchema(
            subject=payload.subject,
            recipients=payload.recipients,
            body=body,
            subtype=subtype,
            attachments=payload.attachments,
            cc=payload.cc,
            bcc=payload.bcc,
            reply_to=payload.reply_to
        )

    async def send_email_async(
        self,
        payload: EmailPayload,
        template_name: Optional[str] = None,
        subtype: MessageType = MessageType.html
    ) -> bool:
        """
        Асинхронная отправка email.
        Подходит для вызова внутри асинхронных функций FastAPI.
        """
        message = self._prepare_message(payload, template_name, subtype)
        try:
            await self.fastmail.send_message(message, template_name=template_name)
            logger.info(f"Email '{payload.subject}' успешно отправлен получателям: {payload.recipients}")
            return True
        except ConnectionErrors as e:
            logger.error(f"Ошибка подключения при отправке email '{payload.subject}': {e}", exc_info=True)
            return False
        except Exception as e:
            logger.critical(f"Непредвиденная ошибка при отправке email '{payload.subject}': {e}", exc_info=True)
            return False

    def send_email_background(
        self,
        background_tasks: BackgroundTasks,
        payload: EmailPayload,
        template_name: Optional[str] = None,
        subtype: MessageType = MessageType.html
    ) -> None:
        """
        Отправка email в фоновом режиме с использованием BackgroundTasks от FastAPI.
        Позволяет немедленно вернуть ответ клиенту, не дожидаясь завершения отправки.
        """
        message = self._prepare_message(payload, template_name, subtype)
        background_tasks.add_task(
            self.fastmail.send_message,
            message,
            template_name=template_name
        )
        logger.info(f"Задача отправки email '{payload.subject}' добавлена в фоновые задачи FastAPI.")
