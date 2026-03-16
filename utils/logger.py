import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from .config import BASE_DIR


def setup_logging() -> None:
    """Configure application-wide logging (console + rotating file)."""

    logs_dir = BASE_DIR / "logs"
    logs_dir.mkdir(exist_ok=True)
    log_file = logs_dir / "bot.log"

    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=5 * 1024 * 1024,  # 5 MB
        backupCount=3,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

