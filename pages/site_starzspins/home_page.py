"""
Главная страница starzspins.com после авторизации.

Содержит кнопку кошелька — при клике перехватывает API ответ
со списком провайдеров и передаёт его в PaymentPage.
"""

import allure

from pages.base_page import BasePage
from pages.site_starzspins.payment_page import PaymentPage

# Кнопка кошелька в шапке — появляется после авторизации
WALLET_BUTTON = "//button[@aria-label='Wallet']"

# Часть URL API который возвращает список доступных платёжных провайдеров.
# Запрос уходит в момент открытия модального окна кошелька.
PROVIDERS_API = "/api/deposit/get_providers"


class HomePage(BasePage):

    def open_wallet(self) -> "PaymentPage":
        """
        Кликает на кнопку кошелька и перехватывает ответ API со списком провайдеров.
        Возвращает PaymentPage с сохранённым ответом для последующей проверки провайдера.
        """
        with allure.step("Открываем кошелёк и перехватываем список провайдеров"):
            # После клика URL меняется на ?modal=wallet&tab=deposit
            # API запрос уходит в момент клика — обработчик регистрируется до клика
            response = self.click_and_capture_response(
                WALLET_BUTTON,
                lambda r: PROVIDERS_API in r.url,
            )
        return PaymentPage(self.page, response)
