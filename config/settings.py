import json
import os
from typing import Any
from urllib.parse import urlparse

# Путь к файлу с кредами — живёт в корне проекта рядом с conftest.py
CREDENTIALS_FILE = os.path.join(os.path.dirname(__file__), "..", "credentials.json")


class Settings:
    """Настройки проекта — загружаются из credentials.json"""

    def __init__(self):
        data = self._load_credentials()
        s = data.get("settings", {})

        # false — браузер с окном (удобно для отладки), true — без окна (для CI)
        self.HEADLESS: bool = s.get("headless", False)

        # Задержка между действиями в мс — 0 в нормальном режиме, 500-1000 для наблюдения
        self.SLOW_MO: int = s.get("slow_mo", 0)

        # Список известных адресов крипто-кошельков
        # Используется в паттерне 3 — когда провайдер неизвестен, но кошелёк проверить надо
        self.KNOWN_WALLETS: list[str] = s.get("known_wallets", [])

    @classmethod
    def get_credentials(cls, url: str) -> dict[str, str]:
        """
        Возвращает логин и пароль для переданного URL.

        Нормализует URL до чистого домена перед поиском — убирает схему (https://),
        www. и trailing slash. Это позволяет писать в credentials.json просто "site.com"
        независимо от того в каком формате записан BASE_URL в тестовом файле.

        Примеры нормализации:
          "https://www.starzspins.com/?modal=login" → "starzspins.com"
          "https://365sms.com/"                     → "365sms.com"
          "https://bet25.com"                       → "bet25.com"

        Если домен не найден в credentials.json — возвращает запись "default".
        Если credentials.json не существует — падает с FileNotFoundError.

        Возвращает словарь: {"login": "...", "password": "..."}
        """
        credentials = cls._load_credentials()
        domain = cls._normalize_domain(url)

        if domain in credentials:
            return credentials[domain]

        if "default" in credentials:
            return credentials["default"]

        raise ValueError(
            f"Домен '{domain}' не найден в credentials.json и нет записи 'default'. "
            f"Добавь домен или запись default в credentials.json."
        )

    @classmethod
    def validate(cls) -> None:
        """
        Проверяет что credentials.json существует и содержит запись default.
        Падает с FileNotFoundError если файла нет, с ValueError если нет записи default.
        """
        credentials = cls._load_credentials()
        if "default" not in credentials:
            raise ValueError(
                "credentials.json не содержит запись 'default'. "
                "Добавь её как fallback для сайтов без отдельных кредов."
            )

    @staticmethod
    def _load_credentials() -> dict[str, Any]:
        """Загружает credentials.json. Падает с FileNotFoundError если файла нет."""
        path = os.path.normpath(CREDENTIALS_FILE)
        if not os.path.exists(path):
            raise FileNotFoundError(
                f"Файл credentials.json не найден: {path}\n"
                f"Скопируй credentials.example.json → credentials.json и заполни данными."
            )
        with open(path, encoding="utf-8") as f:
            return json.load(f)

    @staticmethod
    def _normalize_domain(url: str) -> str:
        """
        Приводит URL к чистому домену для поиска в credentials.json.

        Убирает схему (http://, https://), www. и игнорирует path, query и fragment.
        Порт сохраняется (site.com:8080 → site.com:8080) — такой домен нужно
        прописывать в credentials.json вместе с портом.

        Примеры:
          "https://www.site.com/?modal=login" → "site.com"
          "https://site.com/login"            → "site.com"
          "http://site.com:8080"              → "site.com:8080"
          "site.com"                          → "site.com"
        """
        # Если передали просто домен без схемы — добавляем её чтобы urlparse не запутался
        if not url.startswith(("http://", "https://")):
            url = "https://" + url

        domain = urlparse(url).netloc  # вычленяем host (+ port если есть) из URL
        domain = domain.removeprefix("www.")  # убираем www.
        return domain.lower()


# Синглтон — импортируется во все модули, чтобы не создавать объект каждый раз
settings = Settings()
