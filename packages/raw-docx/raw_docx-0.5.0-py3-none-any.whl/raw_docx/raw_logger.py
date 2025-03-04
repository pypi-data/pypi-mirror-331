import sys
import logging
from pathlib import Path
from typing import Optional
from pythonjsonlogger import jsonlogger


class RawLogger:
    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not RawLogger._initialized:
            self.logger = logging.getLogger("raw_docx")
            self.logger.setLevel(logging.INFO)

            # Create JSON formatter
            formatter = jsonlogger.JsonFormatter(
                fmt="%(asctime)s %(name)s %(levelname)s %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )

            # Console handler
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)

            RawLogger._initialized = True

    def setup_file_logging(self, log_dir: Optional[str] = None):
        """Setup file logging in addition to console logging"""
        if log_dir:
            log_path = Path(log_dir)
            log_path.mkdir(parents=True, exist_ok=True)
            file_handler = logging.FileHandler(log_path / "raw_docx.log")
            file_handler.setFormatter(
                jsonlogger.JsonFormatter(
                    fmt="%(asctime)s %(name)s %(levelname)s %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S",
                )
            )
            self.logger.addHandler(file_handler)

    def info(self, message: str):
        """Log info message"""
        self.logger.info(message)

    def warning(self, message: str):
        """Log warning message"""
        self.logger.warning(message)

    def error(self, message: str):
        """Log error message"""
        self.logger.error(message)

    def exception(self, message: str, exc: Exception):
        """Log exception with message"""
        self.logger.exception(message, exc_info=exc)


# Create singleton instance
logger = RawLogger()
