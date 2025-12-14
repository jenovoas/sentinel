import logging
import logging.config
import os

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        },
        "detailed": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(funcName)s() - %(message)s",
        },
    },
    "handlers": {
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stderr",
        },
        "file": {
            "formatter": "detailed",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "logs/sentinel.log",
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5,
        },
    },
    "loggers": {
        "": {
            "handlers": ["default", "file"],
            "level": "INFO",
        },
        "uvicorn": {
            "handlers": ["default"],
            "level": "INFO",
            "propagate": False,
        },
        "sqlalchemy": {
            "handlers": ["default"],
            "level": "WARNING",
            "propagate": False,
        },
    },
}


def setup_logging(level: str = "INFO"):
    """Setup logging configuration"""
    try:
        # Ensure logs directory exists
        os.makedirs("logs", exist_ok=True)
    except (PermissionError, OSError):
        # If we can't create logs dir, disable file handler
        print("⚠️ Warning: Cannot write to logs directory, disabling file logging")
        LOGGING_CONFIG["loggers"][""]["handlers"] = ["default"]

    try:
        LOGGING_CONFIG["loggers"][""]["level"] = level
        logging.config.dictConfig(LOGGING_CONFIG)
    except ValueError as e:
        # If logging config fails, fall back to basic setup
        print(f"⚠️ Warning: Logging config failed: {e}, using basic logging")
        logging.basicConfig(level=getattr(logging, level, logging.INFO))

    return logging.getLogger(__name__)
