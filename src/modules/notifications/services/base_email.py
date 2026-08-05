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
    def __init__(self, fastmail: FastMail, background_tasks: BackgroundTasks):
        self.fastmail = fastmail
        self.background_tasks = background_tasks

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

    async def send_rendered_email_async(
        self,
        recipients: list[str],
        subject: str,
        html: str,
    ) -> bool:
        payload = EmailPayload(recipients=cast(list[NameEmail | str], recipients), subject=subject, body=html)
        message = MessageSchema(
            subject=payload.subject,
            recipients=payload.recipients,  # type: ignore[arg-type]
            body=html,
            subtype=MessageType.html,
        )
        try:
            await self.fastmail.send_message(message)
            return True
        except ConnectionErrors as e:
            logger.error(f"Error during sending email '{subject}': {e}", exc_info=True)
            return False
        except Exception as e:
            logger.error(f"Something went wrong during sending email '{subject}': {e}", exc_info=True)
            return False

    def send_rendered_email_background(
        self,
        recipients: list[str],
        subject: str,
        html: str,
    ) -> list:
        payload = EmailPayload(recipients=cast(list[NameEmail | str], recipients), subject=subject, body=html)
        message = MessageSchema(
            subject=payload.subject,
            recipients=payload.recipients,  # type: ignore[arg-type]
            body=html,
            subtype=MessageType.html,
        )
        self.background_tasks.add_task(self.fastmail.send_message, message)
        logger.info(f"Send email task '{subject}' added to background tasks FastAPI.")
        return self.background_tasks.tasks

    def send_email_background(
        self,
        payload: EmailPayload,
        template_name: str | None = None,
        subtype: MessageType = MessageType.html
    ) -> list:
        """
        Send email in the background using FastAPI BackgroundTasks.
        Returns the response to the client immediately without waiting for the email to be sent.
        """
        message = self._prepare_message(payload, subtype)
        self.background_tasks.add_task(
            self.fastmail.send_message,
            message,
            template_name=template_name
        )
        logger.info(f"Send email task '{payload.subject}' added to background tasks FastAPI.")
        return self.background_tasks.tasks


    @staticmethod
    def build_connection_config(settings: EmailSettings) -> ConnectionConfig:
        return ConnectionConfig(
            MAIL_USERNAME=settings.MAIL_USERNAME,
            MAIL_PASSWORD=settings.MAIL_PASSWORD,
            MAIL_FROM=settings.MAIL_FROM,
            MAIL_PORT=settings.MAIL_PORT,
            MAIL_SERVER=settings.MAIL_SERVER,
            MAIL_FROM_NAME=settings.MAIL_FROM_NAME,
            MAIL_STARTTLS=settings.MAIL_STARTTLS,
            MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
            USE_CREDENTIALS=settings.USE_CREDENTIALS,
            VALIDATE_CERTS=settings.VALIDATE_CERTS,
            TEMPLATE_FOLDER=settings.TEMPLATE_FOLDER,
            SUPPRESS_SEND=settings.SUPPRESS_SEND,
        )
