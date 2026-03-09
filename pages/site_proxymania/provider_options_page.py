"""
Страница провайдера Heleket с выбором валюты и сети для proxymania.su.

Выбирает USDT и TRON (TRC-20), затем переводит поток
на финальную страницу оплаты с реквизитами.
"""

import allure

from pages.base_page import BasePage
from pages.site_proxymania.payment_page import PaymentPage

# Выпадающий список выбора валюты на шаге провайдера
CURRENCY_DROPDOWN = "(//p[text()='Выберите валюту'])[2]"

# Вариант валюты USDT в списке
USDT_OPTION = "//p[text()='USDT']"

# Выпадающий список выбора сети на шаге провайдера
NETWORK_DROPDOWN = "(//p[text()='Выберите сеть'])[2]"

# Вариант сети TRON (TRC-20) в списке
TRON_OPTION = "//p[text()='TRON (TRC-20)']"

# Кнопка перехода на финальный шаг оплаты
GO_TO_PAYMENT_BUTTON = "//span[text()='Перейти к оплате']"


class ProviderOptionsPage(BasePage):

    def select_usdt(self) -> "ProviderOptionsPage":
        """Открывает список валют и выбирает USDT."""
        with allure.step("Выбираем валюту USDT"):
            self.click(CURRENCY_DROPDOWN)
            # После клика отображаются варианты валют
            self.click(USDT_OPTION)
        return self

    def select_tron_network(self) -> "ProviderOptionsPage":
        """Открывает список сетей и выбирает TRON (TRC-20)."""
        with allure.step("Выбираем сеть TRON (TRC-20)"):
            self.click(NETWORK_DROPDOWN)
            # После выбора сети активируется кнопка перехода к оплате
            self.click(TRON_OPTION)
        return self

    def proceed_to_payment(self) -> "PaymentPage":
        """Переходит к финальному шагу оплаты и возвращает итоговую страницу."""
        with allure.step("Переходим к оплате"):
            # После клика происходит ререндер DOM, URL остаётся на домене провайдера
            self.click(GO_TO_PAYMENT_BUTTON)
        return PaymentPage(self.page)
