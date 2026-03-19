from datetime import date, datetime, timedelta
from typing import Dict, List

from services.google_sheets import get_sheets_client


class SlotsCache:

    def __init__(self, ttl_seconds: int = 30):
        self.ttl = ttl_seconds
        self.cache: Dict[str, List[str]] = {}
        self.last_update: Dict[str, datetime] = {}

    def _is_expired(self, key: str) -> bool:
        if key not in self.last_update:
            return True

        return datetime.now() - self.last_update[key] > timedelta(seconds=self.ttl)

    def get_booked_slots(self, booking_date: date) -> List[str]:
        key = booking_date.isoformat()

        # если кэш устарел → обновляем
        if self._is_expired(key):
            gs = get_sheets_client()
            slots = gs.get_booked_times_for_date(booking_date)

            self.cache[key] = slots
            self.last_update[key] = datetime.now()

        return self.cache.get(key, [])

    def invalidate(self, booking_date: date):
        """Сброс кэша после новой записи"""
        key = booking_date.isoformat()

        if key in self.cache:
            del self.cache[key]
        if key in self.last_update:
            del self.last_update[key]


# singleton
_slots_cache: SlotsCache | None = None


def get_slots_cache() -> SlotsCache:
    global _slots_cache

    if _slots_cache is None:
        _slots_cache = SlotsCache()

    return _slots_cache