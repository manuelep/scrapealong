# -*- coding: utf-8 -*-

from . import settings
import logging
from pydal import DAL
import sys

# implement custom loggers form settings.LOGGERS
logger = logging.getLogger(settings.LIB_NAME)
formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s"
)
for item in settings.LOGGERS:
    level, filename = item.split(":", 1)
    if filename in ("stdout", "stderr"):
        handler = logging.StreamHandler(getattr(sys, filename))
    else:
        handler = logging.FileHandler(filename)
    handler.setFormatter(formatter)
    logger.setLevel(getattr(logging, level.upper(), "DEBUG"))
    logger.addHandler(handler)


# connect to db
db = DAL(
    settings.DB_URI,
    folder = settings.DB_FOLDER,
    pool_size = settings.DB_POOL_SIZE,
    migrate = settings.DB_MIGRATE,
    fake_migrate = settings.DB_FAKE_MIGRATE,
)
