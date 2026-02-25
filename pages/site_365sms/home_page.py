import allure
from pages.base_page import BasePage
from pages.site_365sms.deposit_page import DepositPage

# Кнопка пополнения баланса в шапке — появляется после авторизации
PAYMENTS_BUTTON = "//a[@href='/payments']"


class HomePage(BasePage):

    def go_to_payments(self) -> "DepositPage":
        """Переходит на страницу пополнения баланса и возвращает её"""
        with allure.step("Переходим на страницу пополнения баланса"):
            # После клика URL меняется на https://365sms.com/payments
            self.click(PAYMENTS_BUTTON)
        return DepositPage(self.page)