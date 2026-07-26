import logging
from typing import cast

from fastapi import BackgroundTasks
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from fastapi_mail.errors import ConnectionErrors
from pydantic import NameEmail

from modules.notifications.schemas.email_payload import EmailPayload
from modules.notifications.settings import EmailSettings

logger = logging.getLogger("email_service")


class BaseEmailService:
    def __init__(self, settings: EmailSettings, background_tasks: BackgroundTasks):
        self.settings = settings
        self.background_tasks = background_tasks
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
        subtype: MessageType = MessageType.html
    ) -> MessageSchema:
        return MessageSchema(
            subject=payload.subject,
            recipients=cast(list[NameEmail], payload.recipients),
            template_body=payload.body,
            subtype=subtype,
            attachments=payload.attachments or [],
            cc=cast(list[NameEmail], payload.cc or []),
            bcc=cast(list[NameEmail], payload.bcc or []),
            reply_to=cast(list[NameEmail], payload.reply_to or []),
        )

    async def send_email_async(
        self,
        payload: EmailPayload,
        template_name: str | None = None,
        subtype: MessageType = MessageType.html
    ) -> bool:
        message = self._prepare_message(payload, subtype)
        try:
            await self.fastmail.send_message(message, template_name=template_name)
            logger.info(f"Email '{payload.subject}' sent to {payload.recipients} successfully")
            return True
        except ConnectionErrors as e:
            logger.error(f"Error during sending email '{payload.subject}': {e}", exc_info=True)
            return False
        except Exception as e:
            logger.error(f"SomeThing wend wrong during sending email '{payload.subject}': {e}", exc_info=True)
            return False

    def send_email_background(
        self,
        payload: EmailPayload,
        template_name: str | None = None,
        subtype: MessageType = MessageType.html
    ):
        """
        Отправка email в фоновом режиме с использованием BackgroundTasks от FastAPI.
        Позволяет немедленно вернуть ответ клиенту, не дожидаясь завершения отправки.
        """
        message = self._prepare_message(payload, subtype)
        self.background_tasks.add_task(
            self.fastmail.send_message,
            message,
            template_name=template_name
        )
        logger.info(f"Send email task '{payload.subject}' added to background tasks FastAPI.")
        return self.background_tasks.tasks
