"""
Composition root for cross-module dependencies.
Only this layer is allowed to import from multiple modules and wire them together.
"""

from fastapi import BackgroundTasks

from modules.notifications.dependencies import get_users_email_service
from modules.users.ports import UserNotificationPort


async def get_user_notification_service(
    background_tasks: BackgroundTasks,
) -> UserNotificationPort:
    return await get_users_email_service(background_tasks)
