from aiogram import Router, types, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import CommandStart
from aiogram.types import CallbackQuery

from keyboards.inline import main_menu_keyboard
from utils.config import PHONE_NUMBER


router = Router()


@router.message(CommandStart())
async def cmd_start(message: types.Message) -> None:
    text = (
        "Здравствуйте! Шиномонтаж по адресу Рауиса Гареева 110.\n\n"
        "В данном боте вы можете:\n"
        "• посмотреть актуальный прайс\n"
        "• записаться на шиномонтаж\n\n"
        "Время работы: 9:00 – 19:00"
    )
    await message.answer(text, reply_markup=main_menu_keyboard())


@router.callback_query(F.data == "back_to_menu")
async def back_to_menu(callback: CallbackQuery) -> None:
    text = (
        "Здравствуйте! Шиномонтаж по адресу Рауиса Гареева 110.\n\n"
        "В данном боте вы можете:\n"
        "• посмотреть актуальный прайс\n"
        "• записаться на шиномонтаж\n\n"
        "Время работы: 9:00 – 19:00"
    )
    await callback.message.edit_text(text, reply_markup=main_menu_keyboard())
    try:
        await callback.answer()
    except TelegramBadRequest:
        pass


@router.callback_query(F.data == "call")
async def send_phone(callback: CallbackQuery) -> None:
    # В большинстве клиентов Telegram номер в формате +7... автоматически становится кликабельным.
    await callback.message.answer(f"Позвонить: {PHONE_NUMBER}")
    try:
        await callback.answer()
    except TelegramBadRequest:
        pass
