import allure
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
        """Открывает страницу сразу с модалкой логина и возвращает себя для цепочки"""
        with allure.step("Открываем сайт Starzspins с формой входа"):
            self.goto(URL)
        return self

    def login(self, login: str, password: str) -> "WalletPage":
        """Заполняет форму входа и возвращает страницу кошелька после авторизации"""
        from pages.site_starzspins.wallet_page import WalletPage

        with allure.step(f"Вводим логин: {login}"):
            self.fill(LOGIN_INPUT, login)

        with allure.step("Вводим пароль"):
            self.fill(PASSWORD_INPUT, password)

        with allure.step("Нажимаем кнопку входа"):
            self.click(SUBMIT_BUTTON)

        with allure.step("Ожидаем закрытия формы входа"):
            self.wait_for_selector(SUBMIT_BUTTON, state="hidden")

        return WalletPage(self.page)
