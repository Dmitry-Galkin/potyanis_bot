from aiogram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.bot.scheduler import send_class_reminders
from app.config import Config


def setup_scheduler(bot: Bot, config: Config) -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler(timezone="UTC")
    scheduler.add_job(
        send_class_reminders,
        trigger="interval",
        minutes=config.reminder.poll_interval_minutes,
        kwargs={"bot": bot, "config": config},
    )
    scheduler.start()
    return scheduler
