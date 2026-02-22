import os
from dotenv import load_dotenv

# Загружаем переменные из .env файла в окружение процесса
# Должен вызываться до обращения к os.getenv()
load_dotenv()


class Settings:
    """Настройки проекта — загружаются из .env файла"""

    # Учётные данные для авторизации на сайтах — обязательные поля
    LOGIN: str = os.getenv("LOGIN", "")
    PASSWORD: str = os.getenv("PASSWORD", "")

    # false — браузер с окном (удобно для отладки), true — без окна (для CI)
    HEADLESS: bool = os.getenv("HEADLESS", "false").lower() == "true"

    # Задержка между действиями в мс — 0 в нормальном режиме, 500-1000 для наблюдения
    SLOW_MO: int = int(os.getenv("SLOW_MO", "0"))

    @classmethod
    def validate(cls):
        """Проверяет что обязательные переменные заданы в .env"""
        if not cls.LOGIN or not cls.PASSWORD:
            raise ValueError("LOGIN и PASSWORD должны быть заданы в .env файле")


# Синглтон — импортируется во все модули, чтобы не создавать объект каждый раз
settings = Settings()
