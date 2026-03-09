"""
Страница авторизации на proxymania.su.

Открывает главную, вызывает модальную форму входа,
заполняет креды и возвращает NewsPage после авторизации.
"""

import allure

from pages.base_page import BasePage
from pages.site_proxymania import BASE_URL
from pages.site_proxymania.news_page import NewsPage

# Стартовая страница сайта — точка входа в сценарий
URL = BASE_URL + "/"

# Кнопка "Войти" в правой части шапки — открывает модальную форму авторизации
OPEN_LOGIN_BUTTON = "//div[@class='header__right']//a[text()='Войти']"

# Поле ввода логина в модальной форме входа
LOGIN_INPUT = "//input[@id='login-email']"

# Поле ввода пароля в модальной форме входа
PASSWORD_INPUT = "//input[@id='login-password']"

# Кнопка подтверждения входа в модальной форме
SUBMIT_BUTTON = "//button[@id='btn-login']"


class LoginPage(BasePage):

    def open(self) -> "LoginPage":
        """Открывает главную страницу proxymania.su и возвращает себя для цепочки."""
        with allure.step("Открываем сайт proxymania.su"):
            self.goto(URL)
        return self

    def login(self, login: str, password: str) -> "NewsPage":
        """Авторизуется через модальную форму и возвращает страницу новостей."""
        with allure.step("Открываем модальную форму входа"):
            # После клика открывается модальное окно, URL не меняется
            self.click(OPEN_LOGIN_BUTTON)

        with allure.step(f"Вводим логин: {login}"):
            self.fill(LOGIN_INPUT, login)

        with allure.step("Вводим пароль"):
            self.fill(PASSWORD_INPUT, password)

        with allure.step("Подтверждаем вход"):
            # После клика происходит ререндер DOM, URL меняется на /news/
            self.click(SUBMIT_BUTTON)

        return NewsPage(self.page)
