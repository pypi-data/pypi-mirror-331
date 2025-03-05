import logging.config

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {"detailed": {"format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"}},
    "handlers": {"console": {"class": "logging.StreamHandler", "level": "DEBUG", "formatter": "detailed"}},
    "loggers": {
        "automyte": {  # Configure only your library's logger
            "level": "INFO",
            "handlers": ["console"],
            "propagate": False,
        }
    },
}
