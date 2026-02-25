import allure
from playwright.sync_api import Page, Response
from pages.base_page import BasePage

# Название провайдера платёжной интеграции которое ищем в ответе API
# Находится в поле data[].code в JSON ответе /api/deposit/get_providers
PROVIDER_NAME = "Praxis"

# Iframe в котором рендерится платёжная форма внутри модального окна кошелька
PAYMENT_IFRAME = "//iframe[@id='payment-iframe']"

# Кнопка открытия выпадающего списка способов оплаты внутри iframe
PAYMENT_METHOD_DROPDOWN = "//div[@class='custom-select-dropdown-arrow-container']"

# Вариант оплаты USDT TRC-20 в выпадающем списке
USDT_OPTION = "//div[text()='USDT TRC (Tether TRC-20)']"

# Поле ввода суммы пополнения
AMOUNT_INPUT = "//input[@name='amount']"

# Кнопка подтверждения — после нажатия iframe перестраивает DOM с реквизитами
SUBMIT_BUTTON = "//button[@type='submit']"

# Адрес кошелька для перевода — появляется после подтверждения суммы
# Текст содержит пробелы по краям — нужен strip()
WALLET_ADDRESS = "//span[@class='text']"


class PaymentPage(BasePage):
    def __init__(self, page: Page, providers_response: Response):
        super().__init__(page)
        # Ответ API с провайдерами — передаётся из HomePage.open_wallet()
        # is_payment_integration_present() использует его для проверки
        self._providers_response = providers_response
        # frame_locator — ленивый локатор, iframe начинает искать только при первом действии
        self._frame = self.page.frame_locator(PAYMENT_IFRAME)

    def select_usdt_trc20(self) -> "PaymentPage":
        """Открывает дропдаун способов оплаты и выбирает USDT TRC-20"""
        with allure.step("Выбираем способ оплаты: USDT TRC-20"):
            # Открываем выпадающий список способов оплаты
            self._frame.locator(PAYMENT_METHOD_DROPDOWN).click()
            # После клика появляются варианты валют
            self._frame.locator(USDT_OPTION).click()
        return self

    def confirm_amount(self) -> "PaymentPage":
        """Вводит сумму и подтверждает для получения реквизитов кошелька"""
        with allure.step("Вводим сумму и подтверждаем для получения реквизитов"):
            self._frame.locator(AMOUNT_INPUT).fill("300")
            # После клика iframe перестраивает DOM и показывает реквизиты для перевода
            # Страница и модальное окно при этом не ререндерятся, URL не меняется
            self._frame.locator(SUBMIT_BUTTON).click()
        return self

    def is_payment_integration_present(self) -> bool:
        """
        Проверяет наличие нужного провайдера в перехваченном ответе API.
        Ответ был получен в момент открытия кошелька в HomePage.open_wallet().
        Ищет провайдера по полю code в массиве data.
        Возвращает True если провайдер найден, False если нет.
        """
        with allure.step(f"Проверяем наличие провайдера {PROVIDER_NAME} в ответе API"):
            providers = [p["code"] for p in self._providers_response.json().get("data", [])]
            return PROVIDER_NAME in providers

    def attach_wallet_address(self) -> None:
        """Извлекает адрес кошелька из iframe и прикрепляет к allure репорту"""
        with allure.step("Извлекаем адрес кошелька"):
            # Адрес появляется в span после перестройки DOM внутри iframe
            # strip() убирает пробелы по краям которые есть в тексте элемента
            wallet_address = self._frame.locator(WALLET_ADDRESS).inner_text().strip()

        with allure.step(f"Адрес кошелька: {wallet_address}"):
            allure.attach(
                wallet_address or "Адрес не найден",
                name="Адрес кошелька",
                attachment_type=allure.attachment_type.TEXT
            )
