"""
Финальная платёжная форма провайдера Heleket для proxymania.su.

Проверяет наличие логотипа провайдера и извлекает адрес кошелька.
"""

import allure

from pages.base_page import BasePage
from pages.site_proxymania import SITE
import wallet_log

# Логотип провайдера Heleket на финальной платёжной форме
PROVIDER_LOGO = "//*[@href='https://heleket.com']"

# Контейнер с адресом кошелька для перевода на финальном шаге
WALLET_ADDRESS_CONTAINER = "//p[text()='Адрес кошелька для перевода:']/following-sibling::div"


class PaymentPage(BasePage):

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
