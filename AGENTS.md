# AGENTS.md

Этот файл — твоя инструкция. Читай полностью перед тем как писать код.

---

## Паттерн ≠ путь

Паттерн — это только способ проверки интеграции. Их три: по логотипу, по API, по адресу кошелька.

Путь до проверки может быть любым. Количество страниц, порядок шагов, наличие или отсутствие модалок —
всё это определяется конкретным сайтом, а не паттерном.

**Прямая навигация по URL предпочтительна.** Если страница логина, депозита или любой другой шаг доступны
напрямую по URL — открывай через `goto()`, не ищи кнопки в интерфейсе. Это короче, стабильнее и читается лучше.

Примеры когда стоит прыгнуть по URL напрямую:
- Форма входа доступна по `/login` — не нужно идти на главную и кликать кнопку
- Модалка открывается через `?modal=login` — не нужно кликать по кнопке в шапке
- Страница депозита доступна по прямой ссылке после авторизации — не нужно искать кнопку "Deposit"

Если прямой URL недоступен (редиректит на главную, требует предыдущих шагов) — тогда кликай через интерфейс.

---

## Что ты делаешь

Тебе дают сайт и локаторы. Твоя задача — создать страницы и тест.
Больше ничего не трогай.

---

## Что не трогать никогда

- `conftest.py` — отлажен, сложная логика браузерного профиля, сессии и видео при падении
- `wallet_log.py` — общая инфраструктура, не трогать
- `credentials.json` — если существует, не трогать
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
    __init__.py
    login_page.py         ← авторизация (или первый шаг)
    ...промежуточные...   ← столько сколько нужно, можно ноль
    <финальная_страница>.py  ← проверка интеграции и кошелёк, имя по смыслу

tests/
    test_site_название.py
```

Количество страниц в цепочке определяется задачей — не архитектурой.
Один класс страницы = один экран или одно смысловое состояние интерфейса.
Имя финального файла выбирается по смыслу: `payment_page.py` если это форма оплаты провайдера,
`deposit_page.py` если это страница депозита самого сайта.
Смотри раздел "Когда создавать новую страницу".

---

## Когда создавать новую страницу

Создавай новый класс страницы когда:

- **Меняется URL** — редирект или переход на новый адрес. Даже если визуально похоже — это уже другая страница.
  Пример: кнопка в шапке уводит с `https://site.com/` на `https://site.com/deposit` — нужен новый класс.

- **Переход на внешний домен** — полная перезагрузка на домен провайдера.
  Пример: после выбора суммы редирект на `https://pay.provider.com/...` — обязательно новый класс.

- **Смысловое состояние изменилось** — даже если URL не изменился (SPA с ререндером DOM), но пользователь
  перешёл к принципиально другому разделу: авторизация → главная → форма депозита.
  Пример: после логина URL остался `https://site.com/`, но теперь видна шапка с кнопкой кошелька —
  это `HomePage`, а не `LoginPage`.

Не создавай новый класс для каждого клика внутри одного экрана.
Пример: выбор Crypto → USDT → сумма всё на одной странице депозита — это один класс `DepositPage`.

Если пользователь описывает путь пошагово с комментариями о смене URL или ререндере — ориентируйся на его разбивку.

**Модалки через URL.** Если сайт открывает модальное окно (логин, кошелёк) через параметр в URL — открывай его
напрямую через `goto()` вместо клика по кнопке. Это проще и стабильнее.
Пример: вместо `goto("/") → click(SIGN_IN_BUTTON)` используй `goto("/?modal=login")` без лишнего клика.
Если пользователь так и описал путь — делай именно так.

**Iframe внутри модалки — не отдельная страница.** Если после открытия модалки вся дальнейшая работа происходит
внутри iframe (выбор способа оплаты, ввод суммы, адрес кошелька), а URL больше не меняется — это один класс.
Сохраняй `frame_locator` в `self._frame` в `__init__` и используй его для всех действий внутри iframe.

---

## Архитектура

Паттерн — Page Object + цепочка вызовов. Тест читается как сценарий — каждый шаг явный, никаких селекторов, никакого
Playwright напрямую.

```python
# Так выглядит тест — никаких селекторов, никакого Playwright напрямую
deposit_page = (
    LoginPage(self.page)
    .open()
    .login(self.credentials["login"], self.credentials["password"])
    .go_to_deposit()
    .select_crypto()
    .select_usdt()
    .confirm_amount()
)

deposit_page.attach_wallet_address()
assert deposit_page.is_payment_integration_present(...), "..."
```

**Порядок в тесте обязательный**: `attach_wallet_address()` всегда до `assert`.
Кошелёк должен собраться даже если проверка упадёт.

**Сигнатура `is_payment_integration_present` зависит от паттерна** — смотри раздел ниже.

---

## Базовый класс

Все страницы наследуются от `BasePage`. Используй только его методы — не вызывай `self.page.*` напрямую.

Исключение 1 — `frame_locator` для работы с iframe. Сохраняй его в `self._frame` в `__init__` и используй через
`self._frame.locator(...)`.

Исключение 2 — `self.page.expect_navigation()` при редиректах на другой домен. Смотри раздел ниже.

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

## Редиректы на внешний домен — expect_navigation

Если клик вызывает полную перезагрузку страницы с редиректом на другой домен — используй `self.page.expect_navigation()`
напрямую в методе, прямо перед возвратом нового page object.

```python
def confirm_amount(self) -> "PaymentPage":
    """Подтверждает сумму и возвращает страницу платёжной формы провайдера"""
    with allure.step("Подтверждаем сумму"):
        # После клика происходит полная перезагрузка —
        # редирект на внешний домен https://pay.provider.com/...
        # expect_navigation регистрируется ДО клика — иначе быстрый редирект можно пропустить
        with self.page.expect_navigation():
            self.click(CONFIRM_BUTTON)
    return PaymentPage(self.page)
```

**Важно:** не выноси `expect_navigation` в отдельный метод базового класса.
Он чувствителен к уровню вызова в стеке и работает нестабильно через обёртку.
Пиши его всегда inline, непосредственно в методе страницы.

Признаки что нужен `expect_navigation`:
- После клика URL меняется на адрес другого домена
- Пользователь описывает "редирект на сайт провайдера" после подтверждения

Признаки что НЕ нужен:
- Клик открывает модалку или меняет DOM без смены URL (SPA)
- Клик переходит на другую страницу того же домена — Playwright справится сам

---

## Про ожидания

**Playwright ждёт сам.** `fill`, `click`, `get_attribute` — все уже ждут появления и кликабельности элемента. Не
добавляй лишних ожиданий.

Если тест нестабилен — смотри раздел "Если тест падает" ниже.

---

## Маркер clear_session

Добавляй маркер на класс теста если сайт сохраняет авторизацию в браузерном профиле и заходит уже залогиненным.
Маркер всегда принимает `SITE_URL` — константу из того же файла теста.

Ставь по умолчанию без `strategy=` — чистятся только куки, этого достаточно в большинстве случаев.
Добавляй `strategy="full"` только если тест всё равно заходит залогиненным после обычной очистки:

```python
# Дефолт — чистит только куки домена
@pytest.mark.clear_session(SITE_URL)

# Если сайт помнит сессию даже после очистки куков — чистим всё
@pytest.mark.clear_session(SITE_URL, strategy="full")
```

Маркер открывает сайт, чистит куки только конкретного домена (не глобально — глобальная очистка ломает профиль),
и при `strategy="full"` дополнительно чистит все хранилища браузера.

Не добавляй маркер если сайт не сохраняет авторизацию между запусками — лишний `goto()` замедляет тест.

---

## Первый запуск и капча

Некоторые сайты с агрессивной защитой могут выдать капчу при первом запуске на свежем профиле.
Это нормально — профиль постепенно наполняется историей и куками.
При повторном запуске тест перезапустится автоматически до 2 раз (reruns в pytest.ini).

Если тест упал после всех попыток — запусти его повторно вручную:
```bash
pytest --lf --alluredir=reports/allure -v
```

---

## Цикл отладки через PR

После того как открыл PR — пользователь проверяет тест локально. Если что-то не работает, он напишет тебе что именно
упало.

Твой процесс при получении фидбека:

1. Внимательно прочитай что именно упало — степ, ошибка, что видно на видео
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

Трейс недоступен — patchright несовместим с `context.tracing.start()`.
Для отладки используй только видео из allure репорта и логи ошибок.

**Шаг 2 — анализируй причину:**

`TimeoutError` на `click` или `fill` — элемент не появился за отведённое время.
Возможные причины: неверный селектор, страница ещё грузится, элемент внутри iframe.

`TimeoutError` на `click_and_capture_response` — API запрос не был перехвачен.
Возможная причина: запрос уходит до регистрации обработчика. `click_and_capture_response` регистрирует обработчик до
клика — убедись что используешь именно его, а не отдельный `click`.

`TimeoutError` после клика с редиректом на внешний домен — следующий элемент ищется до загрузки новой страницы.
Решение: добавь `with self.page.expect_navigation():` вокруг `self.click(...)` прямо в методе страницы.

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

```python
# test_site_example.py
SITE_URL = "https://example-casino.com"  # ← обязательная константа вверху файла

@pytest.mark.clear_session(SITE_URL, strategy="full")  # если нужна очистка сессии
@allure.feature(SITE_URL)
@allure.story("Платёжная интеграция ProviderName")
class TestExampleCasino(BaseTest):
    ...
```

```python
# payment_page.py
import wallet_log

SITE = "example-casino.com"  # домен — берётся из URL в login_page.py того же сайта


class PaymentPage(BasePage):

    def is_payment_integration_present(self) -> bool:
        """Проверяет наличие логотипа провайдера на странице оплаты"""
        with allure.step("Проверяем наличие логотипа ProviderName"):
            return self.is_first_visible(PROVIDER_LOGO)

    def attach_wallet_address(self) -> None:
        """Извлекает адрес кошелька и прикрепляет к allure репорту"""
        with allure.step("Извлекаем адрес кошелька"):
            wallet_address = self.get_attribute(WALLET_CONTAINER, "...")

        wallet_log.record(SITE, wallet_address)

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
Перехват происходит на любой промежуточной странице через `click_and_capture_response`.
`PaymentPage` получает ответ через конструктор.
Смотри живой пример: `pages/site_starzspins/`

```python
# test_site_example.py
SITE_URL = "https://example-casino.com"  # ← обязательная константа вверху файла

@pytest.mark.clear_session(SITE_URL, strategy="full")
@allure.feature(SITE_URL)
@allure.story("Платёжная интеграция ProviderName")
class TestExampleCasino(BaseTest):
    ...
```

```python
# some_page.py (та страница где уходит нужный запрос)
PROVIDERS_API = "/api/deposit/get_providers"


def open_wallet(self) -> "PaymentPage":
    """Кликает на кнопку и перехватывает список провайдеров"""
    with allure.step("Открываем кошелёк и перехватываем список провайдеров"):
        response = self.click_and_capture_response(
            WALLET_BUTTON,
            lambda r: PROVIDERS_API in r.url
        )
    return PaymentPage(self.page, response)


# payment_page.py
import wallet_log

SITE = "example-casino.com"


class PaymentPage(BasePage):
    def __init__(self, page: Page, providers_response: Response):
        super().__init__(page)
        self._providers_response = providers_response
        self._frame = self.page.frame_locator(PAYMENT_IFRAME)  # если форма в iframe

    def is_payment_integration_present(self) -> bool:
        """Проверяет наличие провайдера в перехваченном ответе API"""
        with allure.step(f"Проверяем наличие провайдера {PROVIDER_NAME} в ответе API"):
            providers = [p["code"] for p in self._providers_response.json().get("data", [])]
            return PROVIDER_NAME in providers

    def attach_wallet_address(self) -> None:
        """Извлекает адрес кошелька и прикрепляет к allure репорту"""
        with allure.step("Извлекаем адрес кошелька"):
            wallet_address = self._frame.locator(WALLET_ADDRESS).inner_text().strip()

        wallet_log.record(SITE, wallet_address)

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
assert payment_page.is_payment_integration_present(), "Провайдер не найден в ответе API"
```

---

### Паттерн 3 — проверка по адресу кошелька

Используется когда провайдера определить невозможно, но кошелёк проверить нужно.
Смотри живой пример: `pages/site_bet25/`

```python
# test_site_example.py
SITE_URL = "https://example-casino.com"  # ← обязательная константа вверху файла

@pytest.mark.clear_session(SITE_URL)
@allure.feature(SITE_URL)
@allure.story("Проверка адреса кошелька USDT")
class TestExampleCasino(BaseTest):
    ...
```

```python
# deposit_page.py
import wallet_log

SITE = "example-casino.com"


class DepositPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self._wallet_address = None

    def attach_wallet_address(self) -> None:
        """Извлекает адрес кошелька и прикрепляет к allure репорту"""
        with allure.step("Извлекаем адрес кошелька"):
            self._wallet_address = self.get_attribute(WALLET_CONTAINER, "...")

        wallet_log.record(SITE, self._wallet_address)

        with allure.step(f"Адрес кошелька: {self._wallet_address}"):
            allure.attach(
                self._wallet_address or "Адрес не найден",
                name="Адрес кошелька",
                attachment_type=allure.attachment_type.TEXT
            )

    def is_payment_integration_present(self, known_wallets: list[str]) -> bool:
        """
        Проверяет что адрес кошелька совпадает с одним из известных.
        known_wallets — список адресов из KNOWN_WALLETS в .env.
        Требует предварительного вызова attach_wallet_address().
        """
        with allure.step("Проверяем адрес кошелька по списку известных"):
            return self._wallet_address in known_wallets
```

```python
# test
from config.settings import settings

deposit_page.attach_wallet_address()
assert deposit_page.is_payment_integration_present(settings.KNOWN_WALLETS), \
    "Адрес кошелька не совпал ни с одним из известных адресов в KNOWN_WALLETS"
```

Список кошельков хранится в `.env`:
```
KNOWN_WALLETS=TKfAamfPa5PDBxTG69jkY2qtZL9QFBXkZj,TXyz456def
```

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

---

## wallet_log — запись кошельков

Каждый page object обязан вызвать `wallet_log.record()` в `attach_wallet_address()`.
Правило: вызов идёт сразу после получения адреса, до `allure.attach()`.

`SITE` — домен сайта: `"365sms.com"`, `"starzspins.com"` и т.д.
Берётся из URL константы в `login_page.py` того же сайта.
