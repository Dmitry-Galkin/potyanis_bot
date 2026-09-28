import asyncio
import json
import logging
import sys
from functools import partial

import numpy as np
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage
from redis.asyncio.client import Redis

from app.bot.filters import IsAdmin, IsAdminOrUser, IsGuest
from app.bot.handlers import admin_router, common_router, guest_router, user_router
from app.bot.interface.interface import setup_commands
from app.bot.middlewares import ConfigMiddleware, LoggingMiddleware
from app.bot.scheduler import setup_scheduler
from app.config.config import load_config
from app.db import migrate
from app.db.schema import init_all_tables


def _default(o):
    """Заглушка для redis, на случай, если придет не сериализуемый тип."""
    if isinstance(o, np.integer):
        return int(o)
    if isinstance(o, np.floating):
        return float(o)
    if isinstance(o, np.ndarray):
        return o.tolist()
    raise TypeError(f"Object of type {o.__class__.__name__} is not JSON serializable")


# Логирование действий пользователей в терминал: время, id, first_name, last_name, username, команда.
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    stream=sys.stdout,
)
logger_actions = logging.getLogger("user_actions")
logger_actions.setLevel(logging.DEBUG)

config = load_config(path_env=".env.dev", path_yaml="config_dev.yaml")
BOT_TOKEN = config.bot.token

redis = Redis(host=config.redis.host, port=config.redis.port)
storage = RedisStorage(
    redis=redis,
    state_ttl=config.redis.state_ttl_seconds,
    data_ttl=config.redis.data_ttl_seconds,
    json_dumps=partial(json.dumps, default=_default),
)

# Создаем объекты бота и диспетчера.
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=storage)

# Сначала логирование, затем подстановка config/bot.
dp.message.outer_middleware(LoggingMiddleware())
dp.callback_query.outer_middleware(LoggingMiddleware())
config_middleware = ConfigMiddleware(config, bot)
dp.message.outer_middleware(config_middleware)
dp.callback_query.outer_middleware(config_middleware)

# Фильтры доступа: админ — только для admin_router, остальное — IsAdminOrUser, гости — guest_router.
is_admin = IsAdmin(bot, config.bot)
is_admin_or_user = IsAdminOrUser(bot, config.bot)
is_guest = IsGuest(bot, config.bot)
admin_router.message.filter(is_admin)
admin_router.callback_query.filter(is_admin)
common_router.message.filter(is_admin_or_user)
common_router.callback_query.filter(is_admin_or_user)
user_router.message.filter(is_admin_or_user)
user_router.callback_query.filter(is_admin_or_user)
guest_router.message.filter(is_guest)
guest_router.callback_query.filter(is_guest)

dp.include_routers(admin_router, common_router, user_router, guest_router)


async def main():
    await setup_commands(bot, bot_config=config.bot)
    await init_all_tables(db_config=config.db)
    # Миграция БД.
    await migrate(db_config=config.db)
    _ = setup_scheduler(bot, config)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
