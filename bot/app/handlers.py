import logging
from io import BytesIO

from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import KeyboardButton, Message, ReplyKeyboardMarkup, WebAppInfo

from app.api import create_product
from app.config import settings

log = logging.getLogger(__name__)
router = Router()


def keyboard(is_admin: bool) -> ReplyKeyboardMarkup:
    rows = [[KeyboardButton(text="Открыть каталог", web_app=WebAppInfo(url=settings.webapp_url))]]
    if is_admin:
        rows.append([KeyboardButton(text="Создать товар")])
    return ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True)


def is_admin(message: Message) -> bool:
    user = message.from_user
    return bool(user and user.id in settings.admin_set())


async def invite(message: Message) -> None:
    user_id = message.from_user.id if message.from_user else None
    log.info("message from %s", user_id)
    await message.answer("У меня есть товар", reply_markup=keyboard(is_admin(message)))


@router.message(CommandStart())
async def start(message: Message) -> None:
    await invite(message)


@router.message(Command("id"))
async def show_id(message: Message) -> None:
    user_id = message.from_user.id if message.from_user else "неизвестно"
    await message.answer(f"Ваш id: {user_id}")


@router.message(Command("create"))
@router.message(F.text == "Создать товар")
async def ask_product(message: Message) -> None:
    if not is_admin(message):
        await invite(message)
        return
    await message.answer("Пришлите одно сообщение: фото и название товара в подписи.")


@router.message(F.photo)
async def save_product(message: Message) -> None:
    if not is_admin(message):
        await invite(message)
        return
    name = (message.caption or "").strip()
    if not name:
        await message.answer("Нужно название в подписи к фото. Пришлите ещё раз одним сообщением.")
        return

    buf = BytesIO()
    await message.bot.download(message.photo[-1], destination=buf)
    try:
        product = await create_product(name, buf.getvalue(), "image/jpeg")
    except Exception:
        log.exception("create product failed")
        await message.answer("Не получилось сохранить товар. Попробуйте ещё раз.")
        return
    await message.answer(f"Товар «{product['name']}» добавлен")


@router.message()
async def fallback(message: Message) -> None:
    await invite(message)
