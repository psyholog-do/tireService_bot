from __future__ import annotations

from datetime import datetime, time, timedelta, date
from typing import List

FIRST_SLOT = time(hour=9, minute=0)
LAST_SLOT = time(hour=18, minute=40)
SLOT_INTERVAL_MINUTES = 20


def generate_daily_slots(booking_date: date) -> List[str]:
    """Generate slots for a specific date with filtering for past time."""

    slots: List[str] = []

    current_dt = datetime.combine(booking_date, FIRST_SLOT)
    last_dt = datetime.combine(booking_date, LAST_SLOT)

    now = datetime.now()

    while current_dt <= last_dt:

        # 🔥 ФИЛЬТР ПРОШЕДШЕГО ВРЕМЕНИ
        if booking_date == now.date():
            if current_dt <= now:
                current_dt += timedelta(minutes=SLOT_INTERVAL_MINUTES)
                continue

        slots.append(current_dt.strftime("%H:%M"))
        current_dt += timedelta(minutes=SLOT_INTERVAL_MINUTES)

    return slots


def get_available_slots_for_date(booking_date: date, booked_times: list[str]) -> List[str]:
    """Return slots that are not already booked and not in the past."""

    all_slots = generate_daily_slots(booking_date)
    booked_set = set(booked_times)

    return [slot for slot in all_slots if slot not in booked_set]
