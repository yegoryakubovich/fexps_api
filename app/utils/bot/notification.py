from aiogram import Bot
from aiogram.exceptions import TelegramForbiddenError

from app.db.models import NotificationStates, Account, NotificationTypes, Actions
from app.repositories import NotificationSettingRepository, NotificationHistoryRepository
from app.services.base import BaseService
from config import settings


class BotNotification:

    def __init__(self):
        self.bot = Bot(token=settings.telegram_token)

    async def send_notification(self, account: Account, notification_type: str, text: str):
        notification_setting = await NotificationSettingRepository().get(account=account)
        if not notification_setting.telegram_id or not notification_setting.is_active:
            return
        if notification_type == NotificationTypes.REQUEST_CHANGE and not notification_setting.is_request_change:
            return
        if notification_type == NotificationTypes.REQUISITE_CHANGE and not notification_setting.is_requisite_change:
            return
        if notification_type == NotificationTypes.ORDER_CHANGE and not notification_setting.is_order_change:
            return
        if notification_type == NotificationTypes.CHAT_CHANGE and not notification_setting.is_chat_change:
            return
        state = NotificationStates.SUCCESS
        try:
            await self.bot.send_message(
                chat_id=notification_setting.telegram_id,
                text=text
            )
        except TelegramForbiddenError:
            state=NotificationStates.BLOCKED
        except ZeroDivisionError:
            state = NotificationStates.ERROR
        notification_history = await NotificationHistoryRepository().create(
            notification_setting=notification_setting,
            type=notification_type,
            state=state,
            text=text,
        )
        await BaseService().create_action(
            model=notification_history,
            action=Actions.CREATE,
            parameters={
                'notification_setting': notification_setting.id,
                'telegram_id': notification_setting.telegram_id,
                'notification_type': notification_type,
                'state': state,
                'text': text,
            },
        )

