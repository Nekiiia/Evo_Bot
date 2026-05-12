import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import config
from database.db import init_db, clear_all_carts
from handlers.user import user_router
from handlers.order import order_router
from products import products  
from aiohttp import web

logging.basicConfig(level=logging.INFO)


async def health_check(request):
    return web.Response(text="Bot is running")

async def start_web():
    app = web.Application()
    app.router.add_get("/", health_check)

    runner = web.AppRunner(app)
    await runner.setup()

    port = int(os.environ.get("PORT", 10000))

    print(f"🌐 Web server running on port {port}")

    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

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

    # запускаем aiohttp сервер
    runner = web.AppRunner(web.Application())
    app = web.Application()
    app.router.add_get("/", lambda r: web.Response(text="Bot is running"))

    runner = web.AppRunner(app)
    await runner.setup()

    port = int(os.environ.get("PORT", 10000))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

    print(f"🌐 Web server running on port {port}")

    # запускаем polling (БЛОКИРУЕТ поток — это нормально)
    await dp.start_polling(bot)