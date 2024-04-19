from dataclasses import dataclass
from environs import Env



@dataclass
class DatabaseConfig:
    host: str          # URL-адрес базы данных
    port: str          # Порт базы данных
    user: str          # Username пользователя базы данных
    password: str      # Пароль к базе данных
    database: str         # Название базы данных


@dataclass
class TgBot:
    token: str            # Токен для доступа к телеграм-боту
    admin_ids: list[int]  # Список id администраторов бота


@dataclass
class Config:
    tg_bot: TgBot
    db: DatabaseConfig


def load_config(path: str | None = None) -> Config:

    env: Env = Env()
    env.read_env(path)

    return Config(
        tg_bot=TgBot(
            token=env('BOT_TOKEN'),
            admin_ids=list(map(int, env.list('ADMIN_IDS')))
        ),
        db=DatabaseConfig(
            host=env('HOST'),
            port=env('PORT'),
            user=env('USER'),
            password=env('PASSWORD'),
            database=env('DATABASE')
        )
    )