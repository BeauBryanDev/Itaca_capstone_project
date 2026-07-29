
from __future__ import annotations
 
import logging
import sys
 
_LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
 
_configured = False
 
 
def setup_logging(debug: bool = False) -> None:
    """Configure the root logger for the application.
 
    """
    global _configured
 
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG if debug else logging.INFO)
 
    if not _configured:
        handler = logging.StreamHandler(stream=sys.stdout)
        handler.setFormatter(logging.Formatter(_LOG_FORMAT, datefmt=_DATE_FORMAT))
        root_logger.addHandler(handler)
        _configured = True

    noisy_loggers = ("uvicorn.access", "tensorflow", "urllib3", "httpx")
    for logger_name in noisy_loggers:
        logging.getLogger(logger_name).setLevel(
            logging.DEBUG if debug else logging.WARNING
        )
 
 
def get_logger(name: str) -> logging.Logger:
    """Return a logger for the given module name.

    """
    return logging.getLogger(name)