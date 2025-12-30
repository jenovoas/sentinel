import json
import logging
import logging.config
import os
from datetime import datetime


class JsonFormatter(logging.Formatter):
    """
    Formateador de logs en formato JSON para Sentinel.
    """
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.utcfromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "filename": record.filename,
            "lineno": record.lineno,
        }
        
        # Incluir Correlation ID si está disponible en el registro
        if hasattr(record, "correlation_id"):
            log_data["correlation_id"] = record.correlation_id
            
        # Incluir excepciones si existen
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
            
        return json.dumps(log_data)


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
        "json": {
            "()": JsonFormatter,
        },
    },
    "handlers": {
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stderr",
        },
        "file": {
            "formatter": "json",
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
    """Configuración de logging estructurado"""
    try:
        # Asegurar que el directorio de logs existe
        os.makedirs("logs", exist_ok=True)
    except (PermissionError, OSError):
        # Si no se puede crear, deshabilitar el handler de archivo
        print("⚠️ Advertencia: No se puede escribir en el directorio de logs, desactivando logging en archivo")
        LOGGING_CONFIG["loggers"][""]["handlers"] = ["default"]

    try:
        LOGGING_CONFIG["loggers"][""]["level"] = level
        logging.config.dictConfig(LOGGING_CONFIG)
    except ValueError as e:
        # Fallback a configuración básica
        print(f"⚠️ Advertencia: Error en la configuración de logs: {e}, usando configuración básica")
        logging.basicConfig(level=getattr(logging, level, logging.INFO))

    return logging.getLogger(__name__)
