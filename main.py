import logging
import asyncio
from aiogram import Bot, Dispatcher
import admin_handlers
import user_handlers
from config import load_config

config = load_config(r'd:\coding\BOT\bot_canteen\.env')


# функция конфигурирования и запуска бота
async def main():
    # регистрируем бота и диспетчер
    bot = Bot(token=config.tg_bot.token)
    dp = Dispatcher()

    '''# Сохранияю данные из .env для передаче данных между модулями в проекте в словаре диспетчера
    dp['host'] = config.db.host
    dp['port'] = config.db.port
    dp['user'] = config.db.user
    dp['password'] = config.db.password
    dp['database'] = config.db.database
    dp['token'] = config.tg_bot.token
    dp['admin_ids'] = config.tg_bot.admin_ids'''

    # регистрируем роутеры в диспетчер
    dp.include_router(admin_handlers.router)
    dp.include_router(user_handlers.router)

    # пропускаем накопившиемя апдейты и запускаем polling
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == '__main__':
    print('Запуск прошел успешно')
    logging.basicConfig(level=logging.DEBUG)
    asyncio.run(main())
