from aiogram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.bot.scheduler.one_time_text import RUN_TIME_DATE, send_one_time_text
from app.bot.scheduler.reminder import send_class_reminders
from app.bot.scheduler.wisdom import send_daily_wisdom
from app.config import Config


def setup_scheduler(bot: Bot, config: Config) -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler(timezone="UTC")
    # Напоминание о предстоящем занятии.
    scheduler.add_job(
        send_class_reminders,
        trigger="interval",
        minutes=config.reminder.poll_interval_minutes,
        kwargs={"bot": bot, "config": config},
    )
    # Ежедневная мудрость.
    scheduler.add_job(
        send_daily_wisdom,
        trigger="cron",
        hour=config.wisdom.send_hour,
        minute=config.wisdom.send_minute,
        timezone=config.time.local_timezone,
        kwargs={"bot": bot, "config": config},
    )
    # Разовое сообщение.
    scheduler.add_job(
        send_one_time_text,
        trigger="date",
        run_date=RUN_TIME_DATE,
        timezone=config.time.local_timezone,
        kwargs={"bot": bot, "config": config},
    )
    scheduler.start()
    return scheduler
