import asyncio
import logging
import sys
from contextlib import asynccontextmanager

import uvicorn
from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand, BotCommandScopeChat, Update
from fastapi import FastAPI, Request

from app.config import settings
from app.handlers import router
from app.storage import StatelessStorage

log = logging.getLogger(__name__)

bot: Bot | None = None
dp: Dispatcher | None = None


def build() -> tuple[Bot, Dispatcher]:
    telegram = Bot(settings.bot_token)
    dispatcher = Dispatcher(storage=StatelessStorage())
    dispatcher.include_router(router)
    return telegram, dispatcher


async def setup_commands(telegram: Bot) -> None:
    base = [BotCommand(command="start", description="Каталог")]
    await telegram.set_my_commands(base)
    admin_commands = base + [BotCommand(command="create", description="Создать товар")]
    for admin_id in settings.admin_set():
        try:
            await telegram.set_my_commands(admin_commands, scope=BotCommandScopeChat(chat_id=admin_id))
        except Exception:
            log.info("команды для %s не записались, кнопка всё равно работает", admin_id)


@asynccontextmanager
async def lifespan(app: FastAPI):
    global bot, dp
    bot, dp = build()
    await setup_commands(bot)
    url = settings.webhook_base.rstrip("/") + "/webhook"
    await bot.set_webhook(url, drop_pending_updates=False)
    log.info("webhook %s", url)
    yield
    await bot.session.close()


app = FastAPI(lifespan=lifespan)


@app.get("/health")
async def health():
    return {"ok": True}


@app.post("/webhook")
async def telegram_webhook(request: Request):
    if bot is None or dp is None:
        return {"ok": False}
    update = Update.model_validate(await request.json(), context={"bot": bot})
    await dp.feed_update(bot, update)
    return {"ok": True}


async def run_polling() -> None:
    telegram, dispatcher = build()
    await setup_commands(telegram)
    await telegram.delete_webhook(drop_pending_updates=False)
    try:
        await dispatcher.start_polling(telegram)
    finally:
        await telegram.session.close()


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    if not settings.bot_token.strip():
        print("BOT_TOKEN пустой, бот не запущен. Каталог в браузере работает без него.")
        return
    try:
        settings.admin_set()
    except ValueError:
        print("ADMIN_IDS: числа через запятую, например 12345,67890")
        sys.exit(1)

    mode = settings.bot_mode.strip().lower()
    if mode == "webhook":
        if not settings.webhook_base.strip():
            print("Для webhook нужен WEBHOOK_BASE, публичный https")
            sys.exit(1)
        uvicorn.run("app.main:app", host="0.0.0.0", port=8080)
        return
    asyncio.run(run_polling())
