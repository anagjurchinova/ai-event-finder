"""
logging_config.py

Centralized logging configuration for the Event Finder application.

- Uses `dictConfig` to define loggers, handlers, and formatters.
- Provides a helper function `configure_logging()` to apply the configuration.
- Logs are structured with timestamp, level, logger name, and message.
"""
import logging
import logging.config

# ------------------------
# Logging Configuration
# ------------------------
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,  # ←  # Critical to allow Flask and other libs to log!
    "formatters": {
        "default": {"format": "%(asctime)s %(levelname)-5s %(name)s: %(message)s"}
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
            "level": "DEBUG"
        }
    },
    "loggers": {
        "app": {
            "level": "DEBUG",
            "propagate": True
        },
        "app.routes": {
            "level": "NOTSET",
            "propagate": True  # so after handling, it passes to "app"
        },
        "app.services": {
            "level": "NOTSET",
            "propagate": True
        },
        "app.repositories": {
            "level": "NOTSET",
            "propagate": True
        },
        "app.util": {
            "level": "NOTSET",
            "propagate": True
        },
        "werkzeug": {
            "level": "ERROR"
        }  # suppress verbose Flask server logs
    },
    "root": {
        "level": "DEBUG",
        "handlers": ["console"]
    }
}


# ------------------------
# Helper Function
# ------------------------
def configure_logging():
    """
       Apply the centralized logging configuration.

       Creates a console handler and applies the LOGGING dictConfig.
       Should be called once at app startup.
       """
    # Create console handler
    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)
    fmt = '%(asctime)s %(levelname)-5s %(name)s: %(message)s'
    console.setFormatter(logging.Formatter(fmt, datefmt='%H:%M:%S'))
    logging.config.dictConfig(LOGGING)
