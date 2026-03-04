"""
Пакет сайта starzspins.com — паттерн 2 (проверка по API ответу).

Определяет BASE_URL и SITE — все остальные модули пакета импортируют их отсюда.
"""

from urllib.parse import urlparse

# Единственное место где определяется домен сайта.
# Все остальные файлы пакета импортируют отсюда — не дублируют строку.
BASE_URL = "https://www.starzspins.com"

# Чистый домен для wallet_log — без схемы и www.
SITE = urlparse(BASE_URL).netloc.removeprefix("www.")
