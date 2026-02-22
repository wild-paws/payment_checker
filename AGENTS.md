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

---

## Что создавать

```
pages/site_название/
    __init__.py         ← пустой файл
    login_page.py       ← авторизация
    ...                 ← страницы навигации (сколько нужно)
    провайдер_page.py   ← проверка интеграции + кошелёк

tests/
    test_site_название.py
```

Страниц навигации может быть сколько угодно — столько сколько шагов до платёжной формы.
Каждая страница возвращает следующую в цепочке.

---

## Архитектура

Паттерн — Page Object + цепочка вызовов. Тест знает только методы страниц, не знает про селекторы.

```python
# Так выглядит тест — никаких селекторов, никакого Playwright напрямую
result_page = (
    LoginPage(self.page)
    .open()
    .login(self.credentials["login"], self.credentials["password"])
    .navigate_to_section()
    .select_crypto()
    .confirm_amount()
)

result_page.attach_wallet_address()
assert result_page.is_payment_integration_present(), "..."
```

**Порядок в тесте обязательный**: `attach_wallet_address()` всегда до `assert`.
Кошелёк должен собраться даже если проверка упадёт.

---

## Базовый класс

Все страницы наследуются от `BasePage`. Используй только его методы — не вызывай `self.page.*` напрямую.

Исключения где `self.page.*` допустим:
- `frame_locator` для работы с iframe
- `expect_response` уже завёрнут в `goto` с predicate — используй его

Доступные методы:

| Метод | Что делает |
|---|---|
| `goto(url)` | Переход на страницу |
| `goto(url, predicate)` | Переход + перехват API ответа, возвращает response |
| `fill(selector, value)` | Ввод текста |
| `click(selector)` | Клик |
| `click_and_wait_for_navigation(selector)` | Клик + ожидание редиректа |
| `wait_for_selector(selector, state)` | Явное ожидание элемента |
| `is_first_visible(selector)` | Видимость первого из найденных элементов |
| `get_attribute(selector, attribute)` | Значение атрибута элемента |

---

## Про ожидания

**Playwright ждёт сам.** `fill`, `click`, `get_attribute` — все уже ждут появления и кликабельности элемента.

Не добавляй `wait_for_selector` перед обычными действиями — это лишнее.

`wait_for_selector` нужен только в одном случае: когда нужно дождаться **исчезновения** элемента.
Пример — ждём закрытия модалки после логина:
```python
self.wait_for_selector(SUBMIT_BUTTON, state="hidden")
```

---

## Если тест падает

Не добавляй ожидания наугад. Сначала разберись где и почему падает.

**Шаг 1 — запроси у пользователя:**
- На каком шаге падает? Какой степ последний в отчёте?
- Какая ошибка? (TimeoutError, AttributeError, AssertionError — это разные проблемы)
- Посмотри видео в Allure отчёте — что происходит на экране в момент падения?
- Открой трейс: скачай `trace.zip` из отчёта и загрузи на https://trace.playwright.dev/ — там видно каждое действие, снапшот DOM и сетевые запросы в момент падения

**Шаг 2 — анализируй причину:**

`TimeoutError` на `click` или `fill` — элемент не появился за отведённое время.
Возможные причины: неверный селектор, страница ещё грузится, элемент в iframe, элемент появляется только после другого действия.

`TimeoutError` на `expect_response` — API запрос не пришёл при переходе на страницу.
Возможная причина: страница открывается кликом, а не через `goto` — ответ уходит до регистрации обработчика.

`AttributeError: 'NoneType'` на `_providers_response.json()` — `open()` не был вызван или API запрос не был перехвачен.

`AssertionError` на `is_payment_integration_present` — интеграция реально отсутствует, либо изменился формат ответа API или селектор логотипа.

**Шаг 3 — если нужно добавить ожидание:**

Добавляй только если понял конкретную причину. Например, если после клика контент подгружается с задержкой и следующий элемент ещё не в DOM — можно добавить `wait_for_selector` перед следующим действием. Но сначала убедись что проблема именно в этом, а не в неверном селекторе.

---

## Два паттерна проверки

### Паттерн 1 — проверка по логотипу

Тест доходит до страницы провайдера и проверяет наличие его логотипа.

```python
# login_page.py — login() возвращает следующую страницу навигации
return NextPage(self.page)

# провайдер_page.py
def is_payment_integration_present(self) -> bool:
    """Проверяет наличие логотипа провайдера на странице"""
    with allure.step("Проверяем наличие логотипа ProviderName"):
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

### Паттерн 2 — проверка по API

Тест перехватывает API ответ при открытии страницы депозита и ищет провайдера в JSON.

```python
# login_page.py — login() вызывает open() ЗДЕСЬ, не в тесте
# open() перехватывает API ответ при переходе на страницу
# если вызвать open() позже — запрос уже ушёл и ответ пропущен
return WalletPage(self.page).open()

# wallet_page.py
def __init__(self, page: Page):
    super().__init__(page)
    self._providers_response = None  # заполняется в open()

def open(self) -> "WalletPage":
    """Открывает страницу депозита и перехватывает список провайдеров"""
    with allure.step("Открываем страницу депозита и перехватываем список провайдеров"):
        self._providers_response = self.goto(URL, lambda r: PROVIDERS_API in r.url)
    return self

def is_payment_integration_present(self) -> bool:
    """Проверяет наличие провайдера в перехваченном ответе API"""
    with allure.step(f"Проверяем наличие провайдера {PROVIDER_NAME} в ответе API"):
        providers = [p["code"] for p in self._providers_response.json().get("data", [])]
        return PROVIDER_NAME in providers
```

Структура JSON может отличаться — смотри в промте или адаптируй под реальный ответ.

---

## Оформление кода

**Константы** — каждая с комментарием что это и когда появляется:
```python
# Кнопка выбора криптовалюты — появляется после выбора способа оплаты
CRYPTO_BUTTON = "//button/span[contains(text(),'CRYPTO')]"
```

**Степы** — каждое действие в `allure.step`, описывай что происходит после:
```python
with allure.step("Выбираем способ оплаты: Crypto"):
    # После клика появляются доступные криптовалюты
    self.click(CRYPTO_BUTTON)
```

**Docstring** — у каждого метода, объясняй что возвращает и зачем:
```python
def navigate_to_deposit(self) -> "DepositPage":
    """Переходит в раздел депозита и возвращает страницу выбора метода оплаты"""
```

**`__init__`** — не добавляй если в нём только `super().__init__(page)`. Python вызовет родительский сам. Нужен только если добавляешь свои атрибуты как в `WalletPage`.

**Аннотации типов** — на всех методах, включая `-> None`.

---

## Пример готового файла

Смотри `pages/site_365sms/checkout_page.py` — паттерн 1, навигация через несколько шагов.
Смотри `pages/site_starzspins/wallet_page.py` — паттерн 2, перехват API + iframe.
