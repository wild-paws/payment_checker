"""
Платёжная форма провайдера Heleket для proxymania.su (паттерн 1).

Выбирает валюту и сеть, переходит к оплате,
проверяет логотип провайдера и сохраняет адрес кошелька.
"""

import allure

from pages.base_page import BasePage
from pages.site_proxymania import SITE
import wallet_log

# Выпадающий список выбора валюты на шаге провайдера
CURRENCY_DROPDOWN = "(//p[text()='Выберите валюту'])[2]"

# Вариант валюты USDT в списке
USDT_OPTION = "//p[text()='USDT']"

# Выпадающий список выбора сети на шаге провайдера
NETWORK_DROPDOWN = "(//p[text()='Выберите сеть'])[2]"

# Вариант сети TRON (TRC-20) в списке
TRON_OPTION = "//p[text()='TRON (TRC-20)']"

# Кнопка перехода к финальному шагу оплаты
GO_TO_PAYMENT_BUTTON = "//span[text()='Перейти к оплате']"

# Логотип провайдера Heleket на платёжной форме
PROVIDER_LOGO = "//*[@href='https://heleket.com']"

# Контейнер с адресом кошелька для перевода на финальном шаге
WALLET_ADDRESS_CONTAINER = "//p[text()='Адрес кошелька для перевода:']/following-sibling::div"


class PaymentPage(BasePage):

    def select_usdt(self) -> "PaymentPage":
        """Открывает список валют и выбирает USDT."""
        with allure.step("Выбираем валюту USDT"):
            self.click(CURRENCY_DROPDOWN)
            # После выбора валюты становится доступен выбор сети
            self.click(USDT_OPTION)
        return self

    def select_tron_network(self) -> "PaymentPage":
        """Открывает список сетей и выбирает TRON (TRC-20)."""
        with allure.step("Выбираем сеть TRON (TRC-20)"):
            self.click(NETWORK_DROPDOWN)
            # После выбора сети активируется кнопка перехода к оплате
            self.click(TRON_OPTION)
        return self

    def proceed_to_payment(self) -> "PaymentPage":
        """Переходит на финальный шаг оплаты и возвращает себя для цепочки."""
        with allure.step("Переходим к оплате"):
            # После клика происходит ререндер DOM, URL остаётся на домене провайдера
            self.click(GO_TO_PAYMENT_BUTTON)
        return self

    def is_payment_integration_present(self) -> bool:
        """Проверяет наличие логотипа Heleket на финальной платёжной форме."""
        with allure.step("Проверяем наличие логотипа Heleket"):
            return self.is_first_visible(PROVIDER_LOGO)

    def attach_wallet_address(self) -> None:
        """Извлекает адрес кошелька, логирует его и прикрепляет к allure."""
        with allure.step("Извлекаем адрес кошелька"):
            wallet_address = self.get_attribute(WALLET_ADDRESS_CONTAINER, "title")

        wallet_log.record(SITE, wallet_address)

        with allure.step(f"Адрес кошелька: {wallet_address}"):
            allure.attach(
                wallet_address or "Адрес не найден",
                name="Адрес кошелька",
                attachment_type=allure.attachment_type.TEXT,
            )
