import os, sys
from typing import List, Tuple, Type, Dict
import datetime
import logging

from sources.workspace import runtime_subdir

class Logger:
    def __init__(self, log_filename):
        self.folder = runtime_subdir("logs")
        self.create_folder(self.folder)
        self.log_path = os.path.join(self.folder, log_filename)
        self.enabled = True
        self.logger = None
        self.last_log_msg = ""
        if self.enabled:
            self.create_logging(log_filename)

    def create_logging(self, log_filename):
        self.logger = logging.getLogger(log_filename)
        self.logger.setLevel(logging.DEBUG)
        self.logger.handlers.clear()
        self.logger.propagate = False
        file_handler = logging.FileHandler(self.log_path)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

    
    def create_folder(self, path):
        """Create log dir"""
        try:
            if not os.path.exists(path):
                os.makedirs(path, exist_ok=True) 
            return True
        except Exception as e:
            self.enabled = False
            return False
    
    def log(self, message, level=logging.INFO):
        if self.last_log_msg == message:
            return
        if self.enabled:
            self.last_log_msg = message
            self.logger.log(level, message)

    def info(self, message):
        self.log(message)

    def error(self, message):
        self.log(message, level=logging.ERROR)

    def warning(self, message):
        self.log(message, level=logging.WARN)

if __name__ == "__main__":
    lg = Logger("test.log")
    lg.log("hello")
    lg2 = Logger("toto.log")
    lg2.log("yo")
    

        