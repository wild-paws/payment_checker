import allure
from pages.base_page import BasePage
from pages.site_onlinesim.payment_page import PaymentPage

# Кнопка пополнения баланса на странице /v2/numbers после авторизации
TOP_UP_BUTTON = "//span[text()='Top up']"


class HomePage(BasePage):

    def go_to_payment(self) -> "PaymentPage":
        """Переходит к форме оплаты и возвращает страницу платежа"""
        with allure.step("Открываем форму пополнения через кнопку Top up"):
            # После клика страница рендерит новый DOM и меняет URL на /v2/payment/
            self.click(TOP_UP_BUTTON)
        return PaymentPage(self.page)
