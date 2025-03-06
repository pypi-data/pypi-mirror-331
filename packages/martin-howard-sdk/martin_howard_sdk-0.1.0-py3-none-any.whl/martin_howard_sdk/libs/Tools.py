import os
import logging
from datetime import datetime


def get_path(filename):
    path = os.path.abspath(filename)
    return path

def log(str):
    logger = logging.getLogger(__name__)
    logger.error(str)

def now():
    data = datetime.now().strftime('%m/%d/%Y %I:%M %p')
    return data

US_DATETIME_FORMAT = '%m/%d/%Y %H:%M:%S'