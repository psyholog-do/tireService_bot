from __future__ import annotations

from datetime import datetime, timedelta

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.date import DateTrigger
from aiogram import Bot


REMINDER_TEXT_TEMPLATE = (
    "Напоминаем!\n\n"
    "Вы записаны на шиномонтаж сегодня в {time}.\n\n"
    "Адрес: Раиса Гареева 110"
)


class ReminderService:
    """Schedules and sends appointment reminders via APScheduler."""

    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        self.scheduler = AsyncIOScheduler()

    def start(self) -> None:
        if not self.scheduler.running:
            self.scheduler.start()

    def schedule_reminder(
        self,
        chat_id: int,
        booking_datetime: datetime,
    ) -> None:
        """Schedule a reminder 1 hour before the booking_datetime."""
        run_at = booking_datetime - timedelta(hours=1)
        now = datetime.now()
        # If the reminder time is in the past, skip scheduling to avoid spam.
        if run_at <= now:
            return

        trigger = DateTrigger(run_date=run_at)
        self.scheduler.add_job(
            self._send_reminder,
            trigger=trigger,
            args=[chat_id, booking_datetime.strftime("%H:%M")],
            misfire_grace_time=300,
        )

    async def _send_reminder(self, chat_id: int, time_str: str) -> None:
        text = REMINDER_TEXT_TEMPLATE.format(time=time_str)
        await self.bot.send_message(chat_id=chat_id, text=text)

