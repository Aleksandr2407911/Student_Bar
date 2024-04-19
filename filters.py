from aiogram.types import Message
from config import load_config

config = load_config(r'd:\coding\BOT\bot_canteen\.env')


def is_admin_filter(message: Message) -> bool:
    return message.from_user.id in config.tg_bot.admin_ids
