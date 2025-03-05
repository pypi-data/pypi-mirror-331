"""
This module is used to manage the logs.
"""

from datetime import datetime

import os

from fastapi import Request

try:
    from env import DEBUG
except ImportError:
    DEBUG = True


class LogManager:
    """
    This class is used to manage the logs.
    """
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

    @staticmethod
    def get_all_levels() -> list:
        """Return all possible levels."""
        return [
            LogManager.DEBUG,
            LogManager.INFO,
            LogManager.WARNING,
            LogManager.ERROR,
            LogManager.CRITICAL,
        ]

    def __init__(self):
        """
        This method is used to initialize the log manager.
        """
        self.file_path = f"logs/data/{datetime.now().strftime('%Y-%m-%d')}.txt"

    def create_log(self, level: str, module: str, request: Request, log: str):
        """
        This method is used to create a log.
        """
        if level not in LogManager.get_all_levels():
            raise ValueError(f"Invalid log level: {level}")
        if level == LogManager.DEBUG and not DEBUG:
            return
        if request is None:
            client_ip = "Unknown"
        else:
            client_ip = request.headers.get("X-Forwarded-For", request.client.host)
        message = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {level} - {module} - {client_ip}] - {log}"
        try:
            with open(self.file_path, "a", encoding="utf-8") as file:
                file.write(f"{message}\n")
        except FileNotFoundError:
            os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
            with open(self.file_path, "w", encoding="utf-8") as file:
                file.write(f"{message}\n")
        print(message)

    def clear_logs(self):
        """
        This method is used to clear the logs.
        """
        with open(self.file_path, "w", encoding="utf-8") as file:
            file.write("")
    
    def get_logs(self) -> list[str]:
        """
        This method is used to get the logs.
        """
        with open(self.file_path, "r", encoding="utf-8") as file:
            return [line.strip() for line in file.readlines()]


log_manager = LogManager()
