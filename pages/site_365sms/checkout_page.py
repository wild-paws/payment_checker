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
        """Переходит к форме оплаты и возвращает страницу платежного шлюза после редиректа."""
        from pages.site_365sms.heleket_page import HeleketPage

        self.click(PAYMENT_BUTTON)
        self.click(CRYPTO_BUTTON)
        self.click(USDT_BUTTON)
        self.click_and_wait_for_navigation(AMOUNT_BUTTON)

        return HeleketPage(self.page)