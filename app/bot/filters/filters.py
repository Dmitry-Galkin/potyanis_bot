from aiogram import Bot
from aiogram.filters import BaseFilter
from aiogram.types import CallbackQuery, Message

from app.bot.roles import UserRole, get_user_role
from app.config.config import BotSettings


def _user_id_from_event(event: Message | CallbackQuery) -> int:
    return event.from_user.id


class IsAdmin(BaseFilter):
    def __init__(self, bot: Bot, bot_config: BotSettings) -> None:
        self.bot = bot
        self.bot_config = bot_config

    async def __call__(self, event: Message | CallbackQuery) -> bool:
        return UserRole.ADMIN == await get_user_role(
            _user_id_from_event(event), self.bot, self.bot_config
        )


class IsUser(BaseFilter):
    def __init__(self, bot: Bot, bot_config: BotSettings) -> None:
        self.bot = bot
        self.bot_config = bot_config

    async def __call__(self, event: Message | CallbackQuery) -> bool:
        return UserRole.USER == await get_user_role(
            _user_id_from_event(event), self.bot, self.bot_config
        )


class IsAdminOrUser(BaseFilter):
    def __init__(self, bot: Bot, bot_config: BotSettings) -> None:
        self.bot = bot
        self.bot_config = bot_config

    async def __call__(self, event: Message | CallbackQuery) -> bool:
        return await get_user_role(
            _user_id_from_event(event), self.bot, self.bot_config
        ) in (UserRole.USER, UserRole.ADMIN)


class IsGuest(BaseFilter):
    """Пользователь не админ и не в группе."""

    def __init__(self, bot: Bot, bot_config: BotSettings) -> None:
        self.bot = bot
        self.bot_config = bot_config

    async def __call__(self, event: Message | CallbackQuery) -> bool:
        return UserRole.GUEST == await get_user_role(
            _user_id_from_event(event), self.bot, self.bot_config
        )
