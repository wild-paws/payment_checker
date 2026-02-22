# AGENTS.md

Этот файл — твоя инструкция. Читай полностью перед тем как писать код.

---

## Что ты делаешь

Тебе дают сайт и локаторы. Твоя задача — создать страницы и тест.
Больше ничего не трогай.

---

## Что не трогать никогда

- `conftest.py` — отлажен, сложная логика видео/трейс при падении
- `pages/base_page.py` — только если нужен новый метод которого реально нет
- `tests/base_test.py`
- `config/settings.py`
- `requirements.txt`
- Существующие сайты в `pages/` и `tests/`
- Не добавляй `@pytest.mark.skip` на тесты которые пишешь — это только для тестов-примеров паттернов

---

## Что создавать

Всегда работай в отдельной ветке — никогда не коммить напрямую в `main`.

Название ветки: `site/название-сайта` (например `site/example-casino`).
Если пользователь не указал название — спроси перед тем как начинать.
После завершения работы открой PR в `main`.

Файлы которые нужно создать:

```
pages/site_название/
    __init__.py       ← пустой файл
    login_page.py     ← авторизация → возвращает HomePage
    home_page.py      ← навигация к оплате → возвращает PaymentPage
    payment_page.py   ← платёжная форма, проверка интеграции, кошелёк

tests/
    test_site_название.py
```

Страниц навигации между `login_page` и `payment_page` может быть больше — столько сколько шагов до платёжной формы.
Каждая возвращает следующую в цепочке.

---

## Архитектура

Паттерн — Page Object + цепочка вызовов. Тест читается как сценарий — каждый шаг явный, никаких селекторов, никакого
Playwright напрямую.

```python
# Так выглядит тест — никаких селекторов, никакого Playwright напрямую
payment_page = (
    LoginPage(self.page)
    .open()
    .click_sign_in()
    .login(self.credentials["login"], self.credentials["password"])
    .go_to_deposit()
    .select_usdt()
)

payment_page.attach_wallet_address()
assert payment_page.is_payment_integration_present(...), "..."
```

**Порядок в тесте обязательный**: `attach_wallet_address()` всегда до `assert`.
Кошелёк должен собраться даже если проверка упадёт.

**Сигнатура `is_payment_integration_present` зависит от паттерна** — смотри раздел ниже.

---

## Базовый класс

Все страницы наследуются от `BasePage`. Используй только его методы — не вызывай `self.page.*` напрямую.

Исключение — `frame_locator` для работы с iframe. Сохраняй его в `self._frame` в `__init__` и используй через
`self._frame.locator(...)`.

Доступные методы:

| Метод                                             | Что делает                                               |
|---------------------------------------------------|----------------------------------------------------------|
| `goto(url)`                                       | Переход на страницу — только для открытия стартового URL |
| `fill(selector, value)`                           | Ввод текста                                              |
| `click(selector)`                                 | Клик                                                     |
| `click_and_capture_response(selector, predicate)` | Клик + перехват API ответа, возвращает response          |
| `is_first_visible(selector)`                      | Видимость первого из найденных элементов                 |
| `get_attribute(selector, attribute)`              | Значение атрибута элемента                               |

---

## Про ожидания

**Playwright ждёт сам.** `fill`, `click`, `get_attribute` — все уже ждут появления и кликабельности элемента. Не
добавляй лишних ожиданий.

Если тест нестабилен — смотри раздел "Если тест падает" ниже.

---

## Цикл отладки через PR

После того как открыл PR — пользователь проверяет тест локально. Если что-то не работает, он напишет тебе что именно
упало.

Твой процесс при получении фидбека:

1. Внимательно прочитай что именно упало — степ, ошибка, что видно на видео или в трейсе
2. Найди причину — не добавляй ожидания наугад, смотри раздел "Если тест падает"
3. Запушь фикс в ту же ветку — пользователь подтянет и перепроверит
4. Не открывай новый PR — работай в том же до полного прохождения теста

---

## Если тест падает

Не добавляй ожидания наугад. Сначала разберись где и почему падает.

**Шаг 1 — запроси у пользователя:**

- На каком шаге падает? Какой степ последний в отчёте?
- Какая ошибка? (`TimeoutError`, `AttributeError`, `AssertionError` — это разные проблемы)
- Посмотри видео в Allure отчёте — что происходит на экране в момент падения?
- Открой трейс: скачай `trace.zip` из отчёта и загрузи на https://trace.playwright.dev/ — там видно каждое действие,
  снапшот DOM и сетевые запросы в момент падения

**Шаг 2 — анализируй причину:**

`TimeoutError` на `click` или `fill` — элемент не появился за отведённое время.
Возможные причины: неверный селектор, страница ещё грузится, элемент внутри iframe.

`TimeoutError` на `click_and_capture_response` — API запрос не был перехвачен.
Возможная причина: запрос уходит до регистрации обработчика. `click_and_capture_response` регистрирует обработчик до
клика — убедись что используешь именно его, а не отдельный `click`.

`AttributeError: 'NoneType'` на `_providers_response.json()` — API ответ не был передан в `PaymentPage`.

`AttributeError: 'NoneType'` на `_wallet_address in known_wallets` — `attach_wallet_address()` не был вызван до
`is_payment_integration_present()`.

`AssertionError` на `is_payment_integration_present` — интеграция реально отсутствует, либо изменился формат ответа
API, селектор логотипа, или адрес кошелька сменился и не обновлён в `KNOWN_WALLETS`.

**Шаг 3 — если нужно добавить ожидание:**

Только если понял конкретную причину. Если после клика следующий элемент появляется с задержкой и Playwright не
успевает — можно добавить `self.page.wait_for_selector(selector)` напрямую. Но сначала убедись что проблема именно в
этом, а не в неверном селекторе.

---

## Три паттерна проверки

### Паттерн 1 — проверка по логотипу

Тест доходит до платёжной формы провайдера и проверяет наличие его логотипа на странице.
Смотри живой пример: `pages/site_365sms/`

```
login_page.login()  →  HomePage
home_page.confirm_amount()  →  PaymentPage
```

```python
# payment_page.py
class PaymentPage(BasePage):

    def is_payment_integration_present(self) -> bool:
        """Проверяет наличие логотипа провайдера на странице оплаты"""
        with allure.step("Проверяем наличие логотипа ProviderName"):
            # is_first_visible берёт первый если селектор находит несколько элементов
            return self.is_first_visible(PROVIDER_LOGO)

    def attach_wallet_address(self) -> None:
        """Извлекает адрес кошелька и прикрепляет к allure репорту"""
        with allure.step("Извлекаем адрес кошелька"):
            wallet_address = self.get_attribute(WALLET_CONTAINER, "title")
        with allure.step(f"Адрес кошелька: {wallet_address}"):
            allure.attach(
                wallet_address or "Адрес не найден",
                name="Адрес кошелька",
                attachment_type=allure.attachment_type.TEXT
            )
```

```python
# test
payment_page.attach_wallet_address()
assert payment_page.is_payment_integration_present(), "Логотип провайдера не найден"
```

---

### Паттерн 2 — проверка по API

Тест перехватывает API ответ в момент клика на кнопку открытия платёжной формы и ищет провайдера в JSON.
Перехват происходит в `HomePage` через `click_and_capture_response`.
`PaymentPage` получает ответ через конструктор.
Смотри живой пример: `pages/site_starzspins/`

```
login_page.login()  →  HomePage
home_page.open_wallet()  →  PaymentPage(page, response)
```

```python
# home_page.py
PROVIDERS_API = "/api/deposit/get_providers"  # часть URL, не полный адрес


def open_wallet(self) -> "PaymentPage":
    """Кликает на кнопку кошелька и перехватывает список провайдеров"""
    with allure.step("Открываем кошелёк и перехватываем список провайдеров"):
        response = self.click_and_capture_response(
            WALLET_BUTTON,
            lambda r: PROVIDERS_API in r.url
        )
    return PaymentPage(self.page, response)


# payment_page.py
class PaymentPage(BasePage):
    def __init__(self, page: Page, providers_response: Response):
        super().__init__(page)
        self._providers_response = providers_response  # передаётся из HomePage
        self._frame = self.page.frame_locator(PAYMENT_IFRAME)  # если форма в iframe

    def is_payment_integration_present(self) -> bool:
        """Проверяет наличие провайдера в перехваченном ответе API"""
        with allure.step(f"Проверяем наличие провайдера {PROVIDER_NAME} в ответе API"):
            providers = [p["code"] for p in self._providers_response.json().get("data", [])]
            return PROVIDER_NAME in providers
```

```python
# test
payment_page.attach_wallet_address()
assert payment_page.is_payment_integration_present(), "Провайдер не найден в ответе API"
```

Структура JSON может отличаться — смотри в промте и адаптируй `is_payment_integration_present()` под реальный ответ.

---

### Паттерн 3 — проверка по адресу кошелька

Используется когда провайдера определить невозможно, но кошелёк проверить нужно.
Тест доходит до адреса кошелька, сохраняет его и сверяет со списком известных адресов из `.env`.
Смотри живой пример: `pages/site_bet25/`

```
login_page.login()  →  HomePage
home_page.select_usdt()  →  PaymentPage
```

```python
# payment_page.py
class PaymentPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        # Адрес кошелька — заполняется в attach_wallet_address()
        # используется в is_payment_integration_present() для проверки
        self._wallet_address = None

    def attach_wallet_address(self) -> None:
        """Извлекает адрес кошелька и прикрепляет к allure репорту"""
        with allure.step("Извлекаем адрес кошелька"):
            self._wallet_address = self.get_attribute(WALLET_CONTAINER, "title")
        with allure.step(f"Адрес кошелька: {self._wallet_address}"):
            allure.attach(
                self._wallet_address or "Адрес не найден",
                name="Адрес кошелька",
                attachment_type=allure.attachment_type.TEXT
            )

    def is_payment_integration_present(self, known_wallets: list[str]) -> bool:
        """
        Проверяет что адрес кошелька совпадает с одним из известных.
        known_wallets — список адресов из переменной KNOWN_WALLETS в .env файле.
        Требует предварительного вызова attach_wallet_address().
        """
        with allure.step("Проверяем адрес кошелька по списку известных"):
            return self._wallet_address in known_wallets
```

```python
# test — импортируй settings и передавай KNOWN_WALLETS явно
from config.settings import settings

payment_page.attach_wallet_address()
assert payment_page.is_payment_integration_present(settings.KNOWN_WALLETS),
    "Адрес кошелька не совпал ни с одним из известных адресов в KNOWN_WALLETS"
```

Список кошельков хранится в `.env`:

```
KNOWN_WALLETS=TKfAamfPa5PDBxTG69jkY2qtZL9QFBXkZj,TXyz456def
```

Если кошелёк сменился — просто добавь новый адрес через запятую, не удаляя старый пока не убедился.

---

## Оформление кода

**Константы** — каждая с комментарием что это и когда появляется:

```python
# Кнопка кошелька в шапке — появляется после авторизации
WALLET_BUTTON = "//button[@aria-label='Wallet']"
```

**Степы** — каждое действие в `allure.step`, описывай что происходит после клика:

```python
with allure.step("Выбираем способ оплаты: USDT TRC-20"):
    # После клика появляется поле ввода суммы
    self._frame.locator(PAYMENT_METHOD_DROPDOWN).click()
```

**Docstring** — у каждого метода, коротко что делает и что возвращает:

```python
def open_wallet(self) -> "PaymentPage":
    """Кликает на кнопку кошелька и перехватывает список провайдеров"""
```

**`__init__`** — не добавляй если только `super().__init__(page)`. Нужен если добавляешь свои атрибуты:

- Паттерн 2 — `_providers_response` и `_frame`
- Паттерн 3 — `_wallet_address`

**Аннотации типов** — на всех методах, включая `-> None`.