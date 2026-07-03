from datetime import UTC

import pandas as pd
from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError

from app.bot.utils import get_datetime_now_utc
from app.config import Config
from app.db.repository import table_select, table_update


def _get_reminder_query(config: Config) -> str:
    """Запрос на получение записей на заданный промежуток времени."""
    query = f"""
        SELECT
            r.id AS registration_id, u.tg_id, s.session_datetime
        FROM
            {config.db.table_registrations} r
        LEFT JOIN
            {config.db.table_sessions} s ON s.id = r.session_id
        LEFT JOIN
            {config.db.table_users} u ON u.id = r.user_id
        WHERE
            r.is_canceled = 0
            AND s.is_actual = 1
            AND r.is_reminded = 0
            AND s.session_datetime BETWEEN ? AND ?
    """
    return query


async def send_class_reminders(bot: Bot, config: Config) -> None:
    # Текущее время.
    now = get_datetime_now_utc()
    # Правая граница.
    upper = str(pd.Timestamp(now) + pd.Timedelta(minutes=config.reminder.lead_minutes))
    # Смотрим на занятия в ближайшее время и кто записан.
    query = _get_reminder_query(config)
    registrations = await table_select(
        db_path=config.db.path,
        query=query,
        parameters=(now, upper),
    )
    # Преобразуем в более удобный формат для случая,
    # когда один пользователь записан более одного раза.
    bookings = {}
    for _, row in registrations.iterrows():
        key = (int(row["tg_id"]), str(row["session_datetime"]))
        if key in bookings:
            bookings[key].append(int(row.registration_id))
        else:
            bookings[key] = [int(row.registration_id)]
    # Шлем сообщения.
    for (tg_id, session_datetime), registration_ids in bookings.items():
        try:
            session_time = (
                pd.Timestamp(session_datetime)
                .tz_localize(UTC)
                .tz_convert(config.time.local_timezone)
                .time()
            )
            hour, minute = str(session_time.hour).zfill(2), str(
                session_time.minute
            ).zfill(2)
            await bot.send_message(
                chat_id=tg_id,
                text=f"Напоминаю: сегодня вы записаны на занятия по йоге в {hour}:{minute}."
                f"\nЖдем вас 🧘",
            )
        except (TelegramForbiddenError, TelegramBadRequest):
            pass  # заблокировал бота / чат недоступен
        # Сразу запишем, что пользователь оповещен.
        # Сделаем это даже для пользователя, которому не смогли отправить сообщение.
        # Скорее всего, у него в настройках стоит запрет и будет бессмысленно пытаться доставить.
        await table_update(
            db_path=config.db.path,
            table=config.db.table_registrations,
            where=f"id IN {tuple(registration_ids)}",
            values={"is_reminded": 1},
        )
