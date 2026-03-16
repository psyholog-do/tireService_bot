import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage

from handlers import start, price, booking, location
from services.reminder_service import ReminderService
from utils.config import BOT_TOKEN
from utils.logger import setup_logging


async def main() -> None:
    setup_logging()
    logger = logging.getLogger(__name__)
    logger.info("Starting Telegram bot...")

    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode="HTML"),
    )
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    reminder_service = ReminderService(bot=bot)
    reminder_service.start()
    logger.info("APScheduler started.")

    # Передаём инстанс сервиса напоминаний в модуль booking
    booking.setup_reminder_service(reminder_service)

    dp.include_router(start.router)
    dp.include_router(price.router)
    dp.include_router(location.router)
    dp.include_router(booking.router)

    logger.info("Bot is ready. Start polling...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
