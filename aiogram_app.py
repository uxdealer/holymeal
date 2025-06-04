import asyncio

from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.utils.exceptions import NetworkError
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app.database.auth_token import AuthToken
from app.database.db_session import async_sessionmaker
from app.database.user import User
from config.settings import get_config

config = get_config()
bot = Bot(token=config.TELEGRAM_BOT_TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=["start"])
async def cmd_start(message: Message):
    async with async_sessionmaker() as session:
        stmt = (
            select(User)
            .options(joinedload(User.tokens))
            .where(User.tg_id == message.chat.id)
        )
        user = (await session.execute(stmt)).scalar()

        if user is None:
            user = User(
                tg_id=message.chat.id,
                username=message.from_user.username or "",
                first_name=message.from_user.first_name or "",
                last_name=message.from_user.last_name or "",
            )
            session.add(user)
            await session.commit()

        auth_token = await AuthToken.generate_auth_token(session, user.id)

        await message.answer(
            text="Привет! Я бот на aiogram.",
            reply_markup=types.InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        types.InlineKeyboardButton(
                            text="Войти",
                            url=f"https://{config.DOMAIN}/auth/{auth_token.token}",
                        )  # type: ignore
                    ]
                ],
            ),
        )


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
