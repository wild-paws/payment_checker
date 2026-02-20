from playwright.sync_api import Page
from pages.base_page import BasePage

URL = "https://365sms.com/"

OPEN_LOGIN_BUTTON = "//a[@data-da-index='4']"
LOGIN_INPUT = "//input[@id='login']"
PASSWORD_INPUT = "//input[@id='password']"
SUBMIT_BUTTON = "//button[@data-action='login']"


class LoginPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)

    def open(self) -> "LoginPage":
        """Открывает главную страницу сайта"""
        super().open(URL)
        return self

    def login(self, login: str, password: str) -> "CheckoutPage":
        """Открывает модалку входа, заполняет форму и выполняет вход"""
        from pages.site_365sms.checkout_page import CheckoutPage

        self.click(OPEN_LOGIN_BUTTON)
        self.fill(LOGIN_INPUT, login)
        self.fill(PASSWORD_INPUT, password)
        self.click(SUBMIT_BUTTON)

        return CheckoutPage(self.page)