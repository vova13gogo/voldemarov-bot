import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from aiogram import Bot, Dispatcher
from aiogram.types import BotCommandScopeDefault
from config import TOKEN
import database
import markov
import settings
from handlers import router
from keyboards import BOT_COMMANDS

async def main():
    await database.init()
    await settings.load()
    await markov.load()

    bot = Bot(token=TOKEN)
    dp = Dispatcher()
    dp.include_router(router)

    await bot.set_my_commands(BOT_COMMANDS, scope=BotCommandScopeDefault())

    print("✅ Бот запущен")
    print(f"📊 Слов в базе: {markov.word_count()}")
    print(f"🎯 Шанс ответа: {settings.get_chance()}%")

    try:
        await dp.start_polling(bot)
    finally:
        await markov.flush()
        await database.close()
        await bot.session.close()
        print("🛑 Бот остановлен, база сохранена")

if __name__ == "__main__":
    asyncio.run(main())
