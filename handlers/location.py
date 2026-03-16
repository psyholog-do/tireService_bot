from aiogram import Router, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery

from utils.config import TELEGRAM_LOCATION_LAT, TELEGRAM_LOCATION_LON


router = Router()


@router.callback_query(F.data == "location")
async def send_location(callback: CallbackQuery) -> None:
    await callback.message.bot.send_location(
        chat_id=callback.message.chat.id,
        latitude=TELEGRAM_LOCATION_LAT,
        longitude=TELEGRAM_LOCATION_LON,
    )
    try:
        await callback.answer()
    except TelegramBadRequest:
        pass
