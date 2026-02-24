import allure
from pages.base_page import BasePage
from pages.site_onlinesim.home_page import HomePage

# Стартовая страница авторизации — после входа редиректит на /v2/numbers
URL = "https://onlinesim.io/auth/login?redirect=/v2/numbers"

# Поле ввода логина на странице авторизации
LOGIN_INPUT = "//input[@id='login']"

# Поле ввода пароля на странице авторизации
PASSWORD_INPUT = "//input[@id='password']"

# Кнопка подтверждения входа — после клика SPA рендерит страницу /v2/numbers
SUBMIT_BUTTON = "//button[contains(@class, 'btn--login')]"


class LoginPage(BasePage):

    def open(self) -> "LoginPage":
        """Открывает страницу авторизации onlinesim.io и возвращает себя для цепочки"""
        with allure.step("Открываем страницу авторизации onlinesim.io"):
            self.goto(URL)
        return self

    def login(self, login: str, password: str) -> "HomePage":
        """Заполняет форму входа и возвращает домашнюю страницу после авторизации"""
        with allure.step(f"Вводим логин: {login}"):
            self.fill(LOGIN_INPUT, login)

        with allure.step("Вводим пароль"):
            self.fill(PASSWORD_INPUT, password)

        with allure.step("Нажимаем кнопку входа"):
            # После клика страница рендерится и URL меняется на /v2/numbers
            self.click(SUBMIT_BUTTON)

        return HomePage(self.page)
