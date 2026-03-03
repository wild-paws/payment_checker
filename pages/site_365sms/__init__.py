from urllib.parse import urlparse

# Единственное место где определяется домен сайта.
# Все остальные файлы пакета импортируют отсюда — не дублируют строку.
BASE_URL = "https://365sms.com"

# Чистый домен для wallet_log — без схемы и www.
SITE = urlparse(BASE_URL).netloc.removeprefix("www.")
