import os
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent

env_path = BASE_DIR / ".env"
if env_path.exists():
    load_dotenv(env_path)
else:
    # Fallback to environment variables only if .env is not present
    load_dotenv()


BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
ADMIN_ID: int | None = int(os.getenv("ADMIN_ID")) if os.getenv("ADMIN_ID") else None
GOOGLE_SHEET_NAME: str = os.getenv("GOOGLE_SHEET_NAME", "")

TELEGRAM_LOCATION_LAT: float = float(os.getenv("TELEGRAM_LOCATION_LAT", "55.725995"))
TELEGRAM_LOCATION_LON: float = float(os.getenv("TELEGRAM_LOCATION_LON", "49.174686"))

PHONE_NUMBER: str = os.getenv("PHONE_NUMBER", "+79991234567")


if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is not set. Please configure it in .env.")

if not GOOGLE_SHEET_NAME:
    raise RuntimeError("GOOGLE_SHEET_NAME is not set. Please configure it in .env.")

