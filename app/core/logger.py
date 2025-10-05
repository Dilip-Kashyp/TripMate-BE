import logging
from logging.handlers import RotatingFileHandler
import sys

# Logger configuration
LOG_FORMAT = "%(levelname)s | %(asctime)s | %(name)s | %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

logger = logging.getLogger("travel_app")
logger.setLevel(logging.INFO)

# Console Handler
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(logging.Formatter(LOG_FORMAT, DATE_FORMAT))

# File Handler (rotating logs)
file_handler = RotatingFileHandler("logs/app.log", maxBytes=5*1024*1024, backupCount=3)
file_handler.setFormatter(logging.Formatter(LOG_FORMAT, DATE_FORMAT))

# Attach handlers
if not logger.handlers:
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
