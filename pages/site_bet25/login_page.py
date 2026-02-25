import allure
from pages.base_page import BasePage
from pages.site_bet25.home_page import HomePage

# Главная страница сайта — точка входа
URL = "https://bet25.com/"

# Ссылка в шапке сайта которая открывает страницу входа
SIGN_IN_BUTTON = "//a[text()='Login']"

# Поле ввода логина на странице входа
LOGIN_INPUT = "//input[@id='login']"

# Поле ввода пароля на странице входа
PASSWORD_INPUT = "//input[@id='password']"

# Кнопка подтверждения входа на странице входа
SUBMIT_BUTTON = "//button[@aria-label='sign in']"


class LoginPage(BasePage):

    def open(self) -> "LoginPage":
        """Открывает главную страницу сайта и возвращает себя для цепочки"""
        with allure.step("Открываем сайт bet25.com"):
            self.goto(URL)
        return self

    def click_sign_in(self) -> "LoginPage":
        """Кликает на ссылку входа и открывает страницу авторизации"""
        with allure.step("Открываем страницу входа"):
            # После клика URL меняется на https://bet25.com/login
            self.click(SIGN_IN_BUTTON)
        return self

    def login(self, login: str, password: str) -> "HomePage":
        """Заполняет форму входа и возвращает главную страницу после авторизации"""
        with allure.step(f"Вводим логин: {login}"):
            self.fill(LOGIN_INPUT, login)

        with allure.step("Вводим пароль"):
            self.fill(PASSWORD_INPUT, password)

        with allure.step("Нажимаем кнопку входа"):
            # После клика происходит ререндер DOM, URL возвращается на https://bet25.com/
            self.click(SUBMIT_BUTTON)

        return HomePage(self.page)
