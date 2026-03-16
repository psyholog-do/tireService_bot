from dataclasses import dataclass
from datetime import date, time, datetime


@dataclass
class Booking:
    """In-memory representation of a booking row stored in Google Sheets."""

    name: str
    phone: str
    car_type: str
    date: date
    time: time
    created_at: datetime
    telegram_id: int

