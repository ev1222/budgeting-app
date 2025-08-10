import logging
from logging.handlers import RotatingFileHandler
import os

# Directory to store logs
LOG_DIR = "./logs"
os.makedirs(LOG_DIR, exist_ok=True)

# Log file path
LOG_FILE = os.path.join(LOG_DIR, "project.log")

# Available log levels
LOG_LEVELS = {
    "NONE": logging.NOTSET,
    "INFO": logging.INFO,
    "DEBUG": logging.DEBUG,
}


def configure_logging(log_level: str = "INFO") -> logging.Logger:
    """
    Configures logging for the entire project, ensuring that ERROR-level
    messages always print.
    """
    level = LOG_LEVELS.get(log_level.upper(), logging.INFO)

    # Set up a logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)  # Use DEBUG to ensure all messages are passed to handlers

    # Clear existing handlers to avoid duplicates
    if logger.hasHandlers():
        logger.handlers.clear()

    # Format for log messages
    formatter = logging.Formatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Console handler (respects the configured log level)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)

    # Dedicated error handler (always prints ERROR+ messages)
    error_handler = logging.StreamHandler()
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)

    # File handler with rotation
    file_handler = RotatingFileHandler(
        LOG_FILE, maxBytes=5 * 1024 * 1024, backupCount=3
    )
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)

    # Add handlers to the logger
    logger.addHandler(console_handler)
    logger.addHandler(error_handler)
    logger.addHandler(file_handler)

    return logger
