import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import config
from database.db import init_db, clear_all_carts
from handlers.user import user_router
from handlers.order import order_router
from products import products  

logging.basicConfig(level=logging.INFO)


async def main():
    await init_db()
    await clear_all_carts()
    print("🧹 Старые корзины очищены | Бот запущен")

    bot = Bot(
        token=config.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher()

    dp.include_router(user_router)
    dp.include_router(order_router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())