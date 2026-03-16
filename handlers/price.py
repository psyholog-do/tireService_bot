from aiogram import Router, types, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery

from keyboards.inline import back_to_menu_keyboard


router = Router()


PRICE_TEXT = (
    "Прайс на шиномонтаж:\n\n"
    "R13–R14 — 1200 ₽\n"
    "R15–R16 — 1400 ₽\n"
    "R17–R18 — 1600 ₽\n"
    "R19–R20 — 2000 ₽\n\n"
    "Дополнительные услуги:\n\n"
    "Балансировка — 300 ₽\n"
    "Подкачка колес — бесплатно"
)


@router.callback_query(F.data == "price")
async def show_price(callback: CallbackQuery) -> None:
    await callback.message.edit_text(PRICE_TEXT, reply_markup=back_to_menu_keyboard())
    try:
        await callback.answer()
    except TelegramBadRequest:
        # query is too old / invalid – безопасно игнорируем
        pass
