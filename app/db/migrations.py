from app.config import DataBaseSettings
from app.db import get_db


async def migrate(db_config: DataBaseSettings):
    # Добавление колонки is_reminded в таблицу registrations.
    # Нужна, чтобы пользователям отправлялись уведомления о заняии один раз.
    await add_is_reminded_column_to_registrations(db_config)


async def add_is_reminded_column_to_registrations(db_config: DataBaseSettings) -> None:
    async with get_db(db_config.path) as db:
        # Посмотрим, есть ли столбец is_reminded в таблице.
        cursor = await db.execute(f"PRAGMA table_info({db_config.table_registrations})")
        columns = [row[1] for row in await cursor.fetchall()]
        if "is_reminded" not in columns:
            await db.execute(
                f"ALTER TABLE {db_config.table_registrations} "
                f"ADD COLUMN is_reminded BOOLEAN NOT NULL DEFAULT 0"
            )
            await db.commit()
