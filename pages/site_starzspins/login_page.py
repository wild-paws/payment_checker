from playwright.sync_api import Page
from pages.base_page import BasePage

URL = "https://www.starzspins.com/?modal=login"

LOGIN_INPUT = "//input[@aria-label='Username or email']"
PASSWORD_INPUT = "//input[@aria-label='Password']"
SUBMIT_BUTTON = "//button[@data-testid='login-submit-btn']"


class LoginPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)

    def open(self) -> "LoginPage":
        """Открывает страницу сразу с модалкой логина"""
        self.goto(URL)
        return self

    def login(self, login: str, password: str) -> "WalletPage":
        """Заполняет форму и выполняет вход, возвращает страницу кошелька"""
        from pages.site_starzspins.wallet_page import WalletPage

        self.fill(LOGIN_INPUT, login)
        self.fill(PASSWORD_INPUT, password)
        self.click(SUBMIT_BUTTON)
        self.wait_for_selector(SUBMIT_BUTTON, state="hidden")

        return WalletPage(self.page)