import allure
from playwright.sync_api import Page
from pages.base_page import BasePage
from pages.site_365sms.checkout_page import CheckoutPage

# Главная страница сайта — точка входа для авторизации
URL = "https://365sms.com/"

# Кнопка в шапке сайта которая открывает модальное окно входа
OPEN_LOGIN_BUTTON = "//a[@data-da-index='4']"

# Поле ввода логина в модальном окне входа
LOGIN_INPUT = "//input[@id='login']"

# Поле ввода пароля в модальном окне входа
PASSWORD_INPUT = "//input[@id='password']"

# Кнопка подтверждения входа в модальном окне
SUBMIT_BUTTON = "//button[@data-action='login']"


class LoginPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)

    def open(self) -> "LoginPage":
        """Открывает главную страницу сайта и возвращает себя для цепочки вызовов"""
        with allure.step("Открываем сайт 365sms.com"):
            # Переходим на главную — форма входа появится после клика на кнопку
            self.goto(URL)
        return self

    def login(self, login: str, password: str) -> "CheckoutPage":
        """Открывает модалку входа, заполняет форму и возвращает страницу пополнения"""
        with allure.step("Открываем форму входа"):
            # Кликаем на кнопку в шапке — появляется модальное окно с формой
            self.click(OPEN_LOGIN_BUTTON)

        with allure.step(f"Вводим логин: {login}"):
            self.fill(LOGIN_INPUT, login)

        with allure.step("Вводим пароль"):
            self.fill(PASSWORD_INPUT, password)

        with allure.step("Нажимаем кнопку входа"):
            # После клика SPA авторизует пользователя без смены URL
            self.click(SUBMIT_BUTTON)

        # SPA не делает редирект — CheckoutPage сам дождётся нужных элементов
        return CheckoutPage(self.page)
