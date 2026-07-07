from dataclasses import dataclass
from typing import List

import yaml
from environs import Env
from marshmallow_dataclass import class_schema


@dataclass
class BotSettings:
    token: str
    group_id: int
    admin_ids: List[int]


@dataclass()
class DataBaseSettings:
    path: str
    table_info: str
    table_templates: str
    table_sessions: str
    table_users: str
    table_registrations: str
    table_days_off: str
    table_wisdom: str


@dataclass
class BookingSettings:
    window_days: int


@dataclass
class TimeSettings:
    local_timezone: str


@dataclass
class RedisSettings:
    host: str
    port: int
    state_ttl_seconds: int
    data_ttl_seconds: int


@dataclass
class ReminderSettings:
    lead_minutes: int
    poll_interval_minutes: int


@dataclass
class WisdomSettings:
    url: str
    model: str
    send_hour: int
    send_minute: int
    api_key: str


@dataclass
class Config:
    bot: BotSettings
    db: DataBaseSettings
    booking: BookingSettings
    time: TimeSettings
    redis: RedisSettings
    reminder: ReminderSettings
    wisdom: WisdomSettings


db_schema = class_schema(DataBaseSettings)()
booking_schema = class_schema(BookingSettings)()
time_schema = class_schema(TimeSettings)()
redis_schema = class_schema(RedisSettings)()
reminder_schema = class_schema(ReminderSettings)()
wisdom_schema = class_schema(WisdomSettings)()


def load_config(path_env: str, path_yaml: str) -> Config:

    env = Env()
    env.read_env(path_env)
    token = env("BOT_TOKEN")
    group_id = int(env("GROUP_ID"))
    admin_ids = [int(idx) for idx in env.list("ADMIN_IDS", default=[])]
    wisdom_api_key = env("DEEPSEEK_API_KEY")

    with open(path_yaml, "r") as input_stream:
        params = yaml.safe_load(input_stream)

    wisdom_params = params["wisdom"]

    config = Config(
        bot=BotSettings(token=token, group_id=group_id, admin_ids=admin_ids),
        db=db_schema.load(params["db"]),
        booking=booking_schema.load(params["booking"]),
        time=time_schema.load(params["time"]),
        redis=redis_schema.load(params["redis"]),
        reminder=reminder_schema.load(params["reminder"]),
        wisdom=WisdomSettings(
            url=wisdom_params["url"],
            model=wisdom_params["model"],
            send_hour=wisdom_params["send_hour"],
            send_minute=wisdom_params["send_minute"],
            api_key=wisdom_api_key,
        ),
    )

    return config
