import allure
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
        """Открывает главную страницу сайта и возвращает себя для цепочки вызовов"""
        with allure.step("Открываем сайт 365sms.com"):
            self.goto(URL)
        return self

    def login(self, login: str, password: str) -> "CheckoutPage":
        """Открывает модалку входа, заполняет форму и возвращает страницу пополнения"""
        from pages.site_365sms.checkout_page import CheckoutPage

        with allure.step("Открываем форму входа"):
            self.click(OPEN_LOGIN_BUTTON)

        with allure.step(f"Вводим логин: {login}"):
            self.fill(LOGIN_INPUT, login)

        with allure.step("Вводим пароль"):
            self.fill(PASSWORD_INPUT, password)

        with allure.step("Нажимаем кнопку входа"):
            self.click(SUBMIT_BUTTON)

        return CheckoutPage(self.page)
