import allure
from playwright.sync_api import Page
from pages.base_page import BasePage

# URL страницы депозита — открывается сразу с нужной вкладкой через query параметры
URL = "https://www.starzspins.com/?modal=wallet&tab=deposit"

# Путь к API который возвращает список доступных платёжных провайдеров
PROVIDERS_API = "/api/deposit/get_providers"

# Название провайдера платёжной интеграции которое ищем в ответе API
PROVIDER_NAME = "Praxis"

# Iframe в котором рендерится платёжная форма
PAYMENT_IFRAME = "//iframe[@id='payment-iframe']"

# Кнопка открытия выпадающего списка способов оплаты внутри iframe
PAYMENT_METHOD_DROPDOWN = "//div[@class='custom-select-dropdown-arrow-container']"

# Вариант оплаты USDT TRC-20 в выпадающем списке
USDT_OPTION = "//div[text()='USDT TRC (Tether TRC-20)']"

# Поле ввода суммы пополнения
AMOUNT_INPUT = "//input[@name='amount']"

# Кнопка подтверждения — после нажатия iframe перезагружается с реквизитами
SUBMIT_BUTTON = "//button[@type='submit']"

# Адрес кошелька для перевода — появляется после подтверждения суммы
# Текст содержит пробелы по краям — нужен strip()
WALLET_ADDRESS = "//span[@class='text']"


class WalletPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        # Ответ API с провайдерами — заполняется в методе open()
        # is_payment_integration_present() использует его для проверки
        self._providers_response = None

    def open(self) -> "WalletPage":
        """
        Открывает страницу депозита и перехватывает ответ API со списком провайдеров.
        Сохраняет ответ в _providers_response для последующей проверки.
        Возвращает себя для цепочки вызовов — вызывается из login_page.login().
        """
        with allure.step("Открываем страницу депозита"):
            self._providers_response = self.goto(URL, lambda r: PROVIDERS_API in r.url)
        return self

    def is_payment_integration_present(self) -> bool:
        """
        Проверяет наличие нужного провайдера в ранее перехваченном ответе API.
        Требует предварительного вызова open() — иначе _providers_response будет None.
        Возвращает True если провайдер найден, False если нет.
        """
        providers = [p["code"] for p in self._providers_response.json().get("data", [])]
        return PROVIDER_NAME in providers

    def attach_wallet_address(self) -> None:
        """
        Ждёт загрузки iframe, выбирает USDT TRC-20, вводит сумму,
        подтверждает и извлекает адрес кошелька из перезагруженного iframe.
        Прикрепляет адрес к allure репорту.
        """
        with allure.step("Ожидаем загрузки платёжного iframe"):
            self.wait_for_selector(PAYMENT_IFRAME)
            frame = self.page.frame_locator(PAYMENT_IFRAME)

        with allure.step("Выбираем способ оплаты: USDT TRC-20"):
            frame.locator(PAYMENT_METHOD_DROPDOWN).click()
            frame.locator(USDT_OPTION).click()

        with allure.step("Вводим сумму и подтверждаем"):
            frame.locator(AMOUNT_INPUT).fill("300")
            frame.locator(SUBMIT_BUTTON).click()

        with allure.step("Извлекаем адрес кошелька"):
            self.wait_for_selector(PAYMENT_IFRAME)
            frame = self.page.frame_locator(PAYMENT_IFRAME)
            wallet_address = frame.locator(WALLET_ADDRESS).inner_text().strip()

        with allure.step(f"Адрес кошелька: {wallet_address}"):
            allure.attach(
                wallet_address or "Адрес не найден",
                name="Адрес кошелька",
                attachment_type=allure.attachment_type.TEXT
            )
