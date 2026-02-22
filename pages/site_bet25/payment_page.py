import allure
from playwright.sync_api import Page
from pages.base_page import BasePage

# Контейнер с адресом кошелька — адрес хранится в атрибуте title элемента p
WALLET_ADDRESS_CONTAINER = "//p[text()='Deposit Address']/following-sibling::div/div/p"


class PaymentPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        # Адрес кошелька — заполняется в attach_wallet_address()
        # используется в is_payment_integration_present() для проверки
        self._wallet_address = None

    def attach_wallet_address(self) -> None:
        """Извлекает адрес кошелька из атрибута title и прикрепляет к allure репорту"""
        with allure.step("Извлекаем адрес кошелька"):
            # Адрес хранится в атрибуте title элемента p под заголовком Deposit Address
            self._wallet_address = self.get_attribute(WALLET_ADDRESS_CONTAINER, "title")

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
        Возвращает True если адрес найден в списке, False если нет.
        """
        with allure.step("Проверяем адрес кошелька по списку известных"):
            return self._wallet_address in known_wallets
