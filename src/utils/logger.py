import logging
import sys
import json
from datetime import datetime
from src.config.settings import settings

class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "func": record.funcName,
            "message": record.getMessage(),
        }
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)
        
        # Add extra context if available
        if hasattr(record, "context"):
            log_record["context"] = record.context
            
        return json.dumps(log_record)

def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        
        if settings.LOG_FORMAT.upper() == "JSON":
            formatter = JsonFormatter()
        else:
            formatter = logging.Formatter(
                '[%(asctime)s] [%(levelname)s] [%(name)s] [%(funcName)s] %(message)s'
            )
            
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(settings.LOG_LEVEL.upper())
        
    return logger

def setup_logging():
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(settings.LOG_LEVEL.upper())
    
    # Add handler to root if not present
    if not root_logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        if settings.LOG_FORMAT.upper() == "JSON":
            formatter = JsonFormatter()
        else:
            formatter = logging.Formatter(
                '[%(asctime)s] [%(levelname)s] [%(name)s] [%(funcName)s] %(message)s'
            )
        handler.setFormatter(formatter)
        root_logger.addHandler(handler)
