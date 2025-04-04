import logging
import os
from datetime import datetime
from logging.handlers import BaseRotatingHandler


# logs are saved to a file which is new every month
class MonthlyRotatingFileHandler(BaseRotatingHandler):
    def __init__(self, directory, suffix="%m-%Y.log"):
        self.directory = directory
        self.suffix = suffix
        self.current_month = datetime.now().strftime(self.suffix)
        log_path = os.path.join(self.directory, self.current_month)
        super().__init__(log_path, mode='a', encoding='utf-8', delay=False)

    def shouldRollover(self, record) -> bool:
        new_month = datetime.now().strftime(self.suffix)
        return new_month != self.current_month

    def doRollover(self):
        self.stream.close()
        self.current_month = datetime.now().strftime(self.suffix)
        new_log_path = os.path.join(self.directory, self.current_month)
        self.baseFilename = os.path.abspath(new_log_path)
        self.stream = self._open()

    def emit(self, record):
        if self.shouldRollover(record):
            self.doRollover()
        super().emit(record)


LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

log_handler = MonthlyRotatingFileHandler(directory=LOG_DIR)
formatter = logging.Formatter("%(asctime)s\t%(levelname)s:\t%(message)s")
log_handler.setFormatter(formatter)

logger = logging.getLogger("AI-APP")
logger.setLevel(logging.INFO)
logger.addHandler(log_handler)
