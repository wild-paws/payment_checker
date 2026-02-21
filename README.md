# Payment Checker

Автоматическая проверка наличия платёжной интеграции на партнёрских сайтах.
Для каждого сайта проверяем что наша платёжка стоит — либо по логотипу на странице, либо по запросу к процессингу.

## Стек

- Python 3.10+
- Playwright (только Chromium)
- pytest
- Allure

## Установка с нуля на Windows

### 1. Установить Python
Скачать с https://python.org и установить.
При установке отметить галку **Add Python to PATH**.

Проверить:
```bash
python --version
```

### 2. Клонировать репозиторий
```bash
git clone https://github.com/твой_юзер/payment_checker.git
cd payment_checker
```

### 3. Создать виртуальное окружение
```bash
python -m venv .venv
.venv\Scripts\activate
```

### 4. Установить зависимости
```bash
pip install -r requirements.txt
```

### 5. Установить Chromium
```bash
playwright install chromium
```

### 6. Создать .env файл с кредами
```bash
copy .env.example .env
```
Открыть `.env` и заполнить:
```
LOGIN=твой_логин
PASSWORD=твой_пароль
HEADLESS=false
SLOW_MO=0
```

### 7. Установить Allure (через Scoop)
```bash
# Установить Scoop если нет
irm get.scoop.sh | iex

# Установить Allure
scoop install allure
```

## Запуск
```bash
# Все тесты с генерацией allure репорта
pytest --alluredir=reports/allure -v

# Открыть allure репорт
allure serve reports/allure

# Один конкретный тест
pytest tests/test_site_365sms.py --alluredir=reports/allure -v
```

## Как добавить новый сайт

### 1. Создать папку для сайта
```
pages/site_название/
```

### 2. Создать `__init__.py`
Пустой файл — нужен чтобы Python видел папку как модуль.

### 3. Создать `login_page.py`
Скопировать из любого существующего сайта и поменять:
- `URL` — ссылка на страницу входа
- Селекторы полей логина, пароля и кнопки входа
- Логику в методе `login` если вход устроен нестандартно (модалка, редирект и т.д.)

### 4. Создать страницу проверки
Скопировать `checkout_page.py` или `wallet_page.py` в зависимости от типа проверки:
- Проверка по логотипу — смотри `site_365sms/heleket_page.py`
- Проверка по API запросу — смотри `site_starzspins/wallet_page.py`

Поменять селекторы и URL под конкретный сайт.

### 5. Создать тест
Скопировать `tests/test_site_365sms.py` и поменять:
- Название файла: `test_site_название.py`
- Название класса: `TestНазвание`
- Импорт `LoginPage` из новой папки
- `@allure.feature` — название сайта
- `@allure.story` — название провайдера платёжки
- `@allure.title` и `@allure.description` — описание теста

## Структура проекта
```
payment_checker/
├── .env                        # креды (не коммитить!)
├── .env.example                # шаблон для .env
├── requirements.txt            # зависимости проекта
├── pytest.ini                  # настройки pytest
├── conftest.py                 # фикстуры: браузер, страница, креды, allure хуки
├── config/
│   └── settings.py             # загрузка настроек из .env
├── pages/
│   ├── base_page.py            # базовый класс с общими методами
│   ├── site_365sms/            # страницы для 365sms.com
│   │   ├── login_page.py       # авторизация
│   │   ├── checkout_page.py    # навигация к платёжной форме
│   │   └── heleket_page.py     # проверка логотипа Heleket
│   └── site_starzspins/        # страницы для starzspins.com
│       ├── login_page.py       # авторизация
│       └── wallet_page.py      # проверка провайдера через API
└── tests/
    ├── base_test.py            # базовый класс тестов
    ├── test_site_365sms.py     # тест для 365sms.com
    └── test_site_starzspins.py # тест для starzspins.com
```