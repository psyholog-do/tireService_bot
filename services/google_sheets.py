from __future__ import annotations

from datetime import datetime, date
from typing import List, Optional

import gspread
from google.auth.transport.requests import AuthorizedSession  # noqa F401

from utils.config import BASE_DIR, GOOGLE_SHEET_NAME


BOOKINGS_HEADER = [
    "Name",
    "Phone",
    "Car Type",
    "Date",
    "Time",
    "Created At",
    "Telegram ID",
]


class GoogleSheetsClient:
    """Optimized wrapper around gspread for booking operations."""

    def __init__(self, sheet_key: str = GOOGLE_SHEET_NAME) -> None:
        credentials_path = BASE_DIR / "credentials.json"

        if not credentials_path.exists():
            raise FileNotFoundError(
                f"credentials.json not found at {credentials_path}. "
                "Download your Google service account credentials and place it there."
            )

        # Connect to Google
        self.gc = gspread.service_account(filename=str(credentials_path))

        # IMPORTANT: open by KEY instead of name (faster, no Drive API required)
        self.sh = self.gc.open_by_key(sheet_key)

        self.worksheet = self.sh.sheet1

        self._ensure_header()

    def _ensure_header(self) -> None:
        """Ensure first row contains correct headers."""
        first_row = self.worksheet.row_values(1)

        if not first_row:
            self.worksheet.append_row(BOOKINGS_HEADER)
            return

        if first_row != BOOKINGS_HEADER:
            # Do nothing to avoid damaging existing data
            return

    def append_booking(
        self,
        name: str,
        phone: str,
        car_type: str,
        booking_date: date,
        booking_time: str,
        telegram_id: int,
    ) -> None:
        """Add booking row to Google Sheets."""

        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        row = [
            name,
            phone,
            car_type,
            booking_date.strftime("%Y-%m-%d"),
            booking_time,
            created_at,
            str(telegram_id),
        ]

        self.worksheet.append_row(row)

    def get_booked_times_for_date(self, booking_date: date) -> List[str]:
        """
        Return list of booked time slots for given date.

        Optimized: reads only required columns instead of whole sheet.
        """

        target_date = booking_date.strftime("%Y-%m-%d")

        dates = self.worksheet.col_values(4)
        times = self.worksheet.col_values(5)

        booked: List[str] = []

        # skip header
        for d, t in zip(dates[1:], times[1:]):
            if d == target_date:
                booked.append(t)

        return booked


# --------------------------------------------------
# Singleton instance (prevents reconnecting each time)
# --------------------------------------------------

_sheets_client: Optional[GoogleSheetsClient] = None


def get_sheets_client() -> GoogleSheetsClient:
    """
    Returns a single shared GoogleSheetsClient instance.

    Prevents multiple connections to Google API
    and makes the bot much faster.
    """

    global _sheets_client

    if _sheets_client is None:
        _sheets_client = GoogleSheetsClient()

    return _sheets_client