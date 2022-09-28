import sys
sys.path.append('..')
import logging
from logging.handlers import TimedRotatingFileHandler
from datetime import datetime

class Logger:
    FORMATTER = logging.Formatter("%(asctime)s — %(name)s — %(levelname)s — %(message)s")
    dt = datetime.now().strftime("%d-%m-%y")
    LOG_FILE = "/tmp/PY-Meshaxon:{}.log".format(dt)

    def __init__(self,loggerName):
        self.logger = logging.getLogger(loggerName)

    def get_logger(self):
        self.logger.setLevel(logging.DEBUG)
        self.logger.addHandler(self.get_console_handler())
        self.logger.addHandler(self.get_file_handler())
        self.logger.propagate = False
        return self.logger

    def get_file_handler(self):
        file_handler = TimedRotatingFileHandler(self.LOG_FILE, when='midnight')
        file_handler.setFormatter(self.FORMATTER)
        return file_handler

    def get_console_handler(self):
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(self.FORMATTER)
        return console_handler
