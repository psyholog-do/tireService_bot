from __future__ import annotations

from datetime import date, timedelta
from typing import Iterable, List

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from utils.config import PHONE_NUMBER


def main_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Прайс", callback_data="price")],
            [InlineKeyboardButton(text="Запись", callback_data="booking:start")],
            [InlineKeyboardButton(text="📍 Как проехать", callback_data="location")],
            # Telegram inline button URL не поддерживает схему tel:,
            # поэтому используем callback и отправляем кликабельный номер в сообщении.
            [InlineKeyboardButton(text="📞 Позвонить", callback_data="call")],
        ]
    )


def back_to_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Назад", callback_data="back_to_menu")],
        ]
    )


def car_type_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Легковая", callback_data="car:Легковая"),
            ],
            [
                InlineKeyboardButton(text="Кроссовер", callback_data="car:Кроссовер"),
            ],
            [
                InlineKeyboardButton(text="Внедорожник", callback_data="car:Внедорожник"),
            ],
        ]
    )
def services_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Шиномонтаж", callback_data="service:tire")],
        [InlineKeyboardButton(text="Балансировка", callback_data="service:balance")],
        [InlineKeyboardButton(text="Комплекс", callback_data="service:full")],
        ]
    )

def booking_date_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Сегодня", callback_data="date:today"),
                InlineKeyboardButton(text="Завтра", callback_data="date:tomorrow"),
            ],
            [
                InlineKeyboardButton(text="Выбрать дату", callback_data="date:custom"),
            ],
        ]
    )


def custom_date_keyboard(days_ahead: int = 30) -> InlineKeyboardMarkup:
    """Inline 'calendar' – buttons with concrete dates for the next N days."""
    today = date.today()
    buttons: List[List[InlineKeyboardButton]] = []
    row: List[InlineKeyboardButton] = []

    for i in range(days_ahead):
        d = today + timedelta(days=i)
        text = d.strftime("%d.%m")
        callback_data = f"date:{d.isoformat()}"
        row.append(InlineKeyboardButton(text=text, callback_data=callback_data))
        if len(row) == 5:
            buttons.append(row)
            row = []

    if row:
        buttons.append(row)

    buttons.append(
        [InlineKeyboardButton(text="Назад", callback_data="booking:date_back")]
    )

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def time_slots_keyboard(slots: Iterable[str]) -> InlineKeyboardMarkup:
    buttons: List[List[InlineKeyboardButton]] = []
    row: List[InlineKeyboardButton] = []
    for slot in slots:
        row.append(InlineKeyboardButton(text=slot, callback_data=f"time:{slot}"))
        if len(row) == 3:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)

    buttons.append(
        [InlineKeyboardButton(text="Назад", callback_data="booking:time_back")]
    )

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def confirm_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Подтвердить", callback_data="booking:confirm"),
            ],
            [
                InlineKeyboardButton(text="Отмена", callback_data="booking:cancel"),
            ],
        ]
    )

