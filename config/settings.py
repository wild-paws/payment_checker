import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    LOGIN: str = os.getenv("LOGIN", "")
    PASSWORD: str = os.getenv("PASSWORD", "")
    HEADLESS: bool = os.getenv("HEADLESS", "false").lower() == "true"
    SLOW_MO: int = int(os.getenv("SLOW_MO", "0"))

    @classmethod
    def validate(cls):
        """Проверяет что обязательные переменные заданы в .env"""
        if not cls.LOGIN or not cls.PASSWORD:
            raise ValueError("LOGIN и PASSWORD должны быть заданы в .env файле")


settings = Settings()
