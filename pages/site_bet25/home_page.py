import allure
from pages.base_page import BasePage
from pages.site_bet25.payment_page import PaymentPage

# Кнопка перехода в раздел депозита — появляется после авторизации
DEPOSIT_BUTTON = "//a[text()='Deposit']"

# Кнопка выбора валюты USDT — появляется после перехода в раздел депозита
USDT_BUTTON = "//div[text()='USDT']"


class HomePage(BasePage):

    def go_to_deposit(self) -> "HomePage":
        """Переходит в раздел депозита и возвращает себя для цепочки"""
        with allure.step("Переходим в раздел депозита"):
            # После клика URL меняется на /account/cashier/deposit
            self.click(DEPOSIT_BUTTON)
        return self

    def select_usdt(self) -> "PaymentPage":
        """Выбирает USDT и возвращает страницу с адресом кошелька"""
        with allure.step("Выбираем валюту: USDT"):
            # После клика URL меняется на /account/cashier/deposit/1076
            # и появляется адрес кошелька для пополнения
            self.click(USDT_BUTTON)
        return PaymentPage(self.page)
