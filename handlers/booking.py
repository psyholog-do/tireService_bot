from __future__ import annotations

from datetime import datetime, date
import logging

from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery

from keyboards.inline import (
    car_type_keyboard,
    booking_date_keyboard,
    custom_date_keyboard,
    time_slots_keyboard,
    confirm_keyboard,
    main_menu_keyboard,
)

from services.google_sheets import get_sheets_client
from services.slot_manager import get_available_slots_for_date
from services.reminder_service import ReminderService
from utils.config import ADMIN_ID


router = Router()
logger = logging.getLogger(__name__)

_reminder_service: ReminderService | None = None


def setup_reminder_service(service: ReminderService) -> None:
    global _reminder_service
    _reminder_service = service


class BookingStates(StatesGroup):
    name = State()
    phone = State()
    car_type = State()
    date = State()
    time = State()


# ----------------------------
# START BOOKING
# ----------------------------

@router.callback_query(F.data == "booking:start")
async def booking_start(callback: CallbackQuery, state: FSMContext):
    logger.info("Booking started by %s", callback.from_user.id)

    await state.clear()
    await state.set_state(BookingStates.name)

    await callback.message.edit_text("Введите ваше имя")
    await callback.answer()


# ----------------------------
# NAME
# ----------------------------

@router.message(BookingStates.name)
async def process_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text.strip())

    await state.set_state(BookingStates.phone)
    await message.answer("Введите номер телефона")


# ----------------------------
# PHONE
# ----------------------------

@router.message(BookingStates.phone)
async def process_phone(message: types.Message, state: FSMContext):
    await state.update_data(phone=message.text.strip())

    await state.set_state(BookingStates.car_type)
    await message.answer(
        "Выберите тип автомобиля",
        reply_markup=car_type_keyboard()
    )


# ----------------------------
# CAR TYPE
# ----------------------------

@router.callback_query(BookingStates.car_type, F.data.startswith("car:"))
async def process_car_type(callback: CallbackQuery, state: FSMContext):

    _, car_type = callback.data.split(":", 1)

    await state.update_data(car_type=car_type)

    # 👇 ПЕРЕХОД К ВЫБОРУ УСЛУГИ
    await state.set_state(BookingStates.service)

    await callback.message.edit_text(
        "Выберите услугу",
        reply_markup=services_keyboard()
    )

    await callback.answer()


# ----------------------------
# SERVICE (NEW)
# ----------------------------

@router.callback_query(BookingStates.service, F.data.startswith("service:"))
async def process_service(callback: CallbackQuery, state: FSMContext):

    _, service_key = callback.data.split(":", 1)

    service_map = {
        "tire": "Шиномонтаж",
        "balance": "Балансировка",
        "full": "Комплекс",
    }

    service = service_map.get(service_key, "Неизвестно")

    await state.update_data(service=service)

    await state.set_state(BookingStates.date)

    await callback.message.edit_text(
        "Выберите дату записи",
        reply_markup=booking_date_keyboard()
    )

    await callback.answer()


# ----------------------------
# DATE
# ----------------------------

@router.callback_query(BookingStates.date, F.data.startswith("date:"))
async def process_date_selection(callback: CallbackQuery, state: FSMContext):

    _, payload = callback.data.split(":", 1)

    if payload == "today":
        selected_date = date.today()

    elif payload == "tomorrow":
        selected_date = date.fromordinal(date.today().toordinal() + 1)

    elif payload == "custom":

        await callback.message.edit_text(
            "Выберите дату",
            reply_markup=custom_date_keyboard()
        )

        await callback.answer()
        return

    else:
        selected_date = date.fromisoformat(payload)

    await state.update_data(date=selected_date.isoformat())

    # ---- GOOGLE SHEETS ----
    gs = get_sheets_client()

    booked_times = gs.get_booked_times_for_date(selected_date)

    available_slots = get_available_slots_for_date(
        selected_date,
        booked_times
    )

    if not available_slots:

        await callback.message.edit_text(
            "На выбранную дату свободных слотов нет.\n\nВыберите другую дату.",
            reply_markup=booking_date_keyboard()
        )

        await callback.answer()
        return

    await state.set_state(BookingStates.time)

    await callback.message.edit_text(
        "Выберите время записи",
        reply_markup=time_slots_keyboard(available_slots)
    )

    await callback.answer()


# ----------------------------
# BACK TO DATE
# ----------------------------

@router.callback_query(BookingStates.time, F.data == "booking:time_back")
async def time_back(callback: CallbackQuery, state: FSMContext):

    await state.set_state(BookingStates.date)

    await callback.message.edit_text(
        "Выберите дату записи",
        reply_markup=booking_date_keyboard()
    )

    await callback.answer()


# ----------------------------
# SELECT TIME
# ----------------------------

@router.callback_query(BookingStates.time, F.data.startswith("time:"))
async def process_time(callback: CallbackQuery, state: FSMContext):

    _, time_str = callback.data.split(":", 1)

    await state.update_data(time=time_str)

    data = await state.get_data()

    human_date = date.fromisoformat(data["date"]).strftime("%d.%m.%Y")

    text = (
        "Подтвердите запись:\n\n"
        f"Имя: {data['name']}\n"
        f"Телефон: {data['phone']}\n"
        f"Тип авто: {data['car_type']}\n"
        f"Дата: {human_date}\n"
        f"Время: {time_str}"
    )

    await callback.message.edit_text(
        text,
        reply_markup=confirm_keyboard()
    )

    await callback.answer()


# ----------------------------
# CANCEL BOOKING
# ----------------------------

@router.callback_query(BookingStates.time, F.data == "booking:cancel")
async def booking_cancel(callback: CallbackQuery, state: FSMContext):

    logger.info("Booking cancelled by %s", callback.from_user.id)

    await state.clear()

    await callback.message.edit_text(
        "Запись отменена.",
        reply_markup=main_menu_keyboard()
    )

    await callback.answer()


# ----------------------------
# CONFIRM BOOKING
# ----------------------------

@router.callback_query(BookingStates.time, F.data == "booking:confirm")
async def booking_confirm(callback: CallbackQuery, state: FSMContext):

    data = await state.get_data()

    booking_date = date.fromisoformat(data["date"])
    booking_time_str = data["time"]

    booking_datetime = datetime.strptime(
        f"{booking_date.isoformat()} {booking_time_str}",
        "%Y-%m-%d %H:%M"
    )

    gs = get_sheets_client()

    # ---- DOUBLE BOOKING PROTECTION ----
    booked_times = gs.get_booked_times_for_date(booking_date)

    if booking_time_str in booked_times:

        await callback.message.edit_text(
            "Этот слот уже заняли. Пожалуйста выберите другое время.",
            reply_markup=booking_date_keyboard()
        )

        await state.set_state(BookingStates.date)
        await callback.answer()
        return

    # ---- SAVE BOOKING ----
    gs.append_booking(
        name=data["name"],
        phone=data["phone"],
        car_type=data["car_type"],
        booking_date=booking_date,
        booking_time=booking_time_str,
        telegram_id=callback.from_user.id,
    )

    # ---- REMINDER ----
    if _reminder_service:

        _reminder_service.schedule_reminder(
            chat_id=callback.message.chat.id,
            booking_datetime=booking_datetime
        )

    human_date = booking_date.strftime("%d.%m.%Y")

    await callback.message.edit_text(
        "Вы успешно записаны!\n\n"
        f"Дата: {human_date}\n"
        f"Время: {booking_time_str}\n\n"
        "Адрес: Рауиса Гареева 110\n\n"
        "Ждём вас!",
        reply_markup=main_menu_keyboard()
    )

    # ---- ADMIN NOTIFICATION ----
    if ADMIN_ID:

        admin_text = (
            "Новая запись!\n\n"
            f"Имя: {data['name']}\n"
            f"Телефон: {data['phone']}\n"
            f"Тип авто: {data['car_type']}\n"
            f"Дата: {human_date}\n"
            f"Время: {booking_time_str}"
        )

        await callback.bot.send_message(
            chat_id=ADMIN_ID,
            text=admin_text
        )

    await state.clear()

    logger.info(
        "Booking confirmed: %s %s (%s)",
        human_date,
        booking_time_str,
        callback.from_user.id
    )

    await callback.answer()