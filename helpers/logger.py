from enum import Enum
import sys

class logLevel(Enum):
    DEBUG = 1,
    ERROR = 2,
    INFO = 3

class Logger:
    def __init__(self, debug: bool=False) -> None:
        self._debug = debug
    
    def print(self, *values, level: logLevel = logLevel.DEBUG):
        if level == logLevel.ERROR:
            print('[ERROR] ', *values, file=sys.stderr)
            return
        
        if level == logLevel.DEBUG and self._debug:
            print('[DEBUG] ', *values)
            return
        
        if level == logLevel.INFO:
            print('[INFO] ', *values)
            return
    
    def error(self, *values):
        self.print(*values, level=logLevel.ERROR)

    def debug(self, *values):
        self.print(*values, level=logLevel.DEBUG)
    
    def info(self, *values):
        self.print(*values, level=logLevel.INFO)