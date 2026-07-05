import logging

from aiogram import Bot
from aiogram.exceptions import TelegramAPIError

from app.bot.services import generate_wisdom
from app.config import Config

logger = logging.getLogger(__name__)


async def send_daily_wisdom(bot: Bot, config: Config) -> None:
    try:
        wisdom_text = await generate_wisdom(config)
    except Exception as e:
        logger.error("Не удалось сгенерировать мудрость: %s", e)
        return
    if not wisdom_text:
        logger.error("Провайдер вернул пустой текст мудрости")
        return
    try:
        text = "🧘‍♂️Время для интересных фактов или просто пофилософствовать\n\n"
        text += wisdom_text
        text += "\n\nP.S. Я еще учусь и иногда могу ошибаться, не верьте мне слепо👨‍🎓"
        await bot.send_message(chat_id=config.bot.group_id, text=text)
    except TelegramAPIError as e:
        logger.error("Не удалось отправить мудрость в беседу: %s", e)
