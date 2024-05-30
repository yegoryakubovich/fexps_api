import asyncio
import logging
from typing import List

from aiogram import Bot
from aiogram.exceptions import TelegramForbiddenError

from app.db.models import NotificationStates, Account, NotificationTypes, Actions, Order, Language, Wallet
from app.repositories import NotificationSettingRepository, NotificationHistoryRepository, WalletAccountRepository, \
    TextRepository, TextTranslationRepository
from app.services.base import BaseService
from config import settings


class BotNotification:

    def __init__(self):
        self.bot = Bot(token=settings.telegram_token)

    @staticmethod
    async def get_text(
            key: str,
            language: Language,
            **kwargs
    ) -> str:
        text = await TextRepository().get(key=key)
        if not text:
            return f'404 {key}'
        translation = await TextTranslationRepository().get(text=text, language=language)
        if not translation:
            return text.value_default.format(**kwargs)
        return translation.value.format(**kwargs)

    async def message_notification(
            self,
            account: Account,
            order: Order,
            text_key: str,
            **kwargs,
    ):
        await self.send_notification_by_wallet(
            wallet=order.request.wallet,
            notification_type=NotificationTypes.CHAT_CHANGE,
            account_id_black_list=[account.id],
            text_key=text_key,
            **kwargs,
        )
        await self.send_notification_by_wallet(
            wallet=order.requisite.wallet,
            notification_type=NotificationTypes.CHAT_CHANGE,
            account_id_black_list=[account.id],
            text_key=text_key,
            **kwargs,
        )

    async def send_notification_by_wallet(
            self,
            wallet: Wallet,
            notification_type: str,
            text_key: str,
            account_id_black_list: list[int] = None,
            **kwargs,
    ):
        if not account_id_black_list:
            account_id_black_list = []
        for account in await WalletAccountRepository().get_accounts_by_wallet(wallet=wallet):
            if account.id in account_id_black_list:
                continue
            await self.send_notification(
                account=account,
                notification_type=notification_type,
                text_key=text_key,
                **kwargs,
            )
            await asyncio.sleep(0.5)

    async def send_notification(
            self,
            account: Account,
            notification_type: str,
            text_key: str,
            **kwargs,
    ):
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
        text = await self.get_text(key=text_key, language=account.language, **kwargs)
        try:
            await self.bot.send_message(chat_id=notification_setting.telegram_id, text=text)
        except TelegramForbiddenError:
            state = NotificationStates.BLOCKED
        except Exception as e:
            logging.critical(e)
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
                'text_key': text_key,
                'text': text,
            },
        )
