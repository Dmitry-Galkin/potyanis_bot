from contextlib import suppress

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message

from app.bot.keyboards.admin import main_admin_keyboard

admin_router = Router()


@admin_router.message(Command(commands="admin"))
async def process_admin_command(message: Message):
    await message.answer(
        text="Выберите, что вы хотите сделать", reply_markup=main_admin_keyboard()
    )


@admin_router.message(Command(commands="get_chat_id"))
async def process_get_chat_id_command(message: Message, **kwargs):
    """Узнать id группы."""
    print(f"---> chat_id: {message.chat.id}")
    await delete_message(kwargs["bot"], message.chat.id, message.message_id)


@admin_router.message(F.chat.type == "private", ~F.text.startswith("/"))
async def send_message_to_chat_from_bot(message: Message, **kwargs):
    """Написать в общую группу от имени бота."""
    # Сообщение только от меня.
    if message.from_user.id == kwargs["config"].bot.admin_ids[0]:
        try:
            await kwargs["bot"].send_message(
                chat_id=kwargs["config"].bot.group_id,
                text=message.text,
            )
        except Exception as e:
            pass


async def delete_message(bot, chat_id: int, message_id: int):
    with suppress(Exception):
        await bot.delete_message(chat_id=chat_id, message_id=message_id)
