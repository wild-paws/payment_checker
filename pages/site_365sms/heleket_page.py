import allure
from playwright.sync_api import Page
from pages.base_page import BasePage

HELEKET_LOGO = "//a[@href='https://heleket.com']"


class HeleketPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)

    def is_payment_integration_present(self) -> bool:
        with allure.step("Ожидаем загрузки платёжной формы Heleket"):
            self.wait_for_selector(HELEKET_LOGO)

        with allure.step("Проверяем наличие логотипа Heleket на странице"):
            return self.is_first_visible(HELEKET_LOGO)
