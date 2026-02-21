from aiogram import Router
from aiogram.types import CallbackQuery, Message

guest_router = Router()

GUEST_MESSAGE = (
    "👋 Вступите в группу, если хотите работать с ботом.\n"
    "https://t.me/+nkehX7aEOfc5NjBi"
)


@guest_router.message()
async def guest_any_message(message: Message) -> None:
    """Ответ гостю (не в группе и не админ): подсказка вступить в группу."""
    await message.answer(GUEST_MESSAGE)


@guest_router.callback_query()
async def guest_any_callback(callback: CallbackQuery) -> None:
    """Ответ гостю при нажатии на кнопку."""
    await callback.answer(GUEST_MESSAGE, show_alert=True)
