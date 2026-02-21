import allure
from playwright.sync_api import Page
from pages.base_page import BasePage

PAYMENT_BUTTON = "//a[@href='/payments']"
CRYPTO_BUTTON = "//button/span[contains(text(),'CRYPTO')]"
USDT_BUTTON = "//button/span[contains(text(),'USDT (TRC20)')]"
AMOUNT_BUTTON = "//button/span[contains(text(),'300₽')]"


class CheckoutPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)

    def navigate_to_payment(self) -> "HeleketPage":
        from pages.site_365sms.heleket_page import HeleketPage

        with allure.step("Переходим на страницу пополнения баланса"):
            self.click(PAYMENT_BUTTON)

        with allure.step("Выбираем способ оплаты: Crypto"):
            self.click(CRYPTO_BUTTON)

        with allure.step("Выбираем валюту: USDT (TRC20)"):
            self.click(USDT_BUTTON)

        with allure.step("Выбираем сумму 300₽ и ждём редиректа на платёжную форму"):
            self.click_and_wait_for_navigation(AMOUNT_BUTTON)

        return HeleketPage(self.page)
