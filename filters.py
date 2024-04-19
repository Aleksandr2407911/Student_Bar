from aiogram.types import Message
from config import load_config

config = load_config('/Users/aleksandrrabinskij/Desktop/Student_Bar/.env')

def is_admin_filter(message: Message) -> bool:
    return message.from_user.id in config.tg_bot.admin_ids
