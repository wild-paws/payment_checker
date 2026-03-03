import allure
from patchright.sync_api import Page
from pages.base_page import BasePage
import wallet_log

# Кнопка выбора валюты USDT — появляется после перехода на страницу депозита
USDT_BUTTON = "//div[text()='USDT']"

# Контейнер с адресом кошелька — адрес хранится в атрибуте value.
# Намеренно широкий локатор: div с атрибутом value уникален на этой странице.
# Появляется после выбора USDT.
WALLET_ADDRESS_CONTAINER = "//div[@value]"

# Идентификатор сайта для wallet_log
SITE = "bet25.com"


class DepositPage(BasePage):
    def __init__(self, page: Page) -> None:
        super().__init__(page)
        # Адрес кошелька — заполняется в attach_wallet_address()
        # используется в is_payment_integration_present() для проверки
        self._wallet_address: str | None = None

    def select_usdt(self) -> "DepositPage":
        """Выбирает USDT и возвращает себя — после клика появляется адрес кошелька"""
        with allure.step("Выбираем валюту: USDT"):
            # После клика на странице появляется адрес кошелька для пополнения
            self.click(USDT_BUTTON)
        return self

    def attach_wallet_address(self) -> None:
        """Извлекает адрес кошелька из атрибута value и прикрепляет к allure репорту"""
        with allure.step("Извлекаем адрес кошелька"):
            self._wallet_address = self.get_attribute(WALLET_ADDRESS_CONTAINER, "value")

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
        known_wallets — список адресов из секции settings.known_wallets в credentials.json.
        Требует предварительного вызова attach_wallet_address().
        Возвращает True если адрес найден в списке, False если нет.
        """
        with allure.step("Проверяем адрес кошелька по списку известных"):
            return self._wallet_address in known_wallets
