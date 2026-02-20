from playwright.sync_api import Page
from pages.base_page import BasePage

HELEKET_LOGO = "//a[@href='https://heleket.com']"


class HeleketPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)

    def is_payment_integration_present(self) -> bool:
        """Проверяет наличие логотипа Heleket на платёжной форме"""
        self.page.wait_for_selector(HELEKET_LOGO)

        return self.page.locator(HELEKET_LOGO).first.is_visible()