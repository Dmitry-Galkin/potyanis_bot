from aiogram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.bot.scheduler.reminder import send_class_reminders
from app.bot.scheduler.wisdom import send_daily_wisdom
from app.config import Config


def setup_scheduler(bot: Bot, config: Config) -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler(timezone="UTC")
    scheduler.add_job(
        send_class_reminders,
        trigger="interval",
        minutes=config.reminder.poll_interval_minutes,
        kwargs={"bot": bot, "config": config},
    )
    scheduler.add_job(
        send_daily_wisdom,
        trigger="cron",
        hour=config.wisdom.send_hour,
        minute=config.wisdom.send_minute,
        timezone=config.time.local_timezone,
        kwargs={"bot": bot, "config": config},
    )
    scheduler.start()
    return scheduler
