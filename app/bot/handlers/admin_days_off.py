from datetime import UTC
from typing import Any, List, Tuple

import pandas as pd
from aiogram import F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup, default_state
from aiogram.types import CallbackQuery, Message

from app.bot.handlers.admin import admin_router
from app.bot.handlers.common import check_owner
from app.bot.keyboards.common import confirm_keyboard
from app.bot.utils import is_date_format_valid
from app.config import Config, DataBaseSettings
from app.db import table_insert, table_select


class FSMAddDaysOff(StatesGroup):
    """Состояния при добавлении отпуска."""

    # Состояние ввода периода отпуска.
    add_days_off_period = State()
    # Состояние подтверждения введенных данных.
    confirm_days_off_period = State()


# Админ нажал кнопку добавить отпуск.
@admin_router.callback_query(F.data == "add_days_off", StateFilter(default_state))
async def start_add_days_off(callback: CallbackQuery, state: FSMContext):
    await state.update_data(owner_id=callback.from_user.id)
    await callback.message.edit_text(
        "⏰ Введите дату или период, на которые хотите добавить отпуск.\n\n"
        "Формат: Год-Месяц-День.\n\n"
        "Например\n"
        "➡️ Для одной даты: \t 2026-01-21\n"
        "➡️ Для периода: \t 2026-01-21  2026-01-24"
    )
    await state.set_state(FSMAddDaysOff.add_days_off_period)


# Админ ввел дату или период.
@admin_router.message(
    FSMAddDaysOff.add_days_off_period,
    ~StateFilter(default_state),
    ~Command(commands="cancel"),
)
async def enter_period(message: Message, state: FSMContext, **kwargs):
    if not await check_owner(message, state):
        return
    dates = message.text.strip().split()
    for n, date in enumerate(dates):
        if not is_date_format_valid(date):
            await message.answer(
                f"❌ Неверный формат {n + 1}-й даты. Пример: 2026-01-21"
            )
            return
    if len(dates) == 1:
        dates.append(dates[0])
    await state.update_data(date_off_start=dates[0])
    await state.update_data(date_off_end=dates[1])
    await message.answer(
        f"📋 Подтвердите отпуск:\n" f"✔️ {dates[0]} - {dates[1]}",
        reply_markup=confirm_keyboard(),
    )
    await state.set_state(FSMAddDaysOff.confirm_days_off_period)


# Админ подтвердил введенную инфу о планируемом отпуске.
@admin_router.callback_query(
    FSMAddDaysOff.confirm_days_off_period,
    F.data == "confirm",
    ~StateFilter(default_state),
)
async def confirm_add(callback: CallbackQuery, state: FSMContext, **kwargs):
    if not await check_owner(callback, state):
        return
    data = await state.get_data()
    await table_insert(
        db_path=kwargs["config"].db.path,
        table=kwargs["config"].db.table_days_off,
        values={
            "date_off_start": data["date_off_start"],
            "date_off_end": data["date_off_end"],
            "is_actual": True,
        },
    )
    await state.clear()
    await callback.message.edit_text("✅ Отпуск успешно добавлен!")
