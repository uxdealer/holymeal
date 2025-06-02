import asyncio

from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.utils.exceptions import NetworkError

API_TOKEN = "6201546479:AAHLpc8X_OvhXUhEUqCYs6hqaV1u8j23Ne0"
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=["start"])
async def cmd_start(message: Message):
    await message.answer("Привет! Я бот на aiogram.")


async def on_bot_shutdown():
    if bot.session is not None:
        await bot.session.close()


def run_aiogram_app():
    from aiogram import executor

    try:
        executor.start_polling(dp, skip_updates=True)
    except NetworkError as e:
        print(f"⚠️ NetworkError: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
    finally:
        asyncio.get_event_loop().run_until_complete(on_bot_shutdown())
