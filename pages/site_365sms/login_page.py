import allure
from pages.base_page import BasePage
from pages.site_365sms.home_page import HomePage

# Стартовая страница сайта — точка входа
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

    def open(self) -> "LoginPage":
        """Открывает главную страницу сайта и возвращает себя для цепочки вызовов"""
        with allure.step("Открываем сайт 365sms.com"):
            # Переходим на главную — форма входа появится после клика на кнопку
            self.goto(URL)
        return self

    def login(self, login: str, password: str) -> "HomePage":
        """Открывает модалку входа, заполняет форму и возвращает главную страницу"""
        with allure.step("Открываем форму входа"):
            # Кликаем на кнопку в шапке — появляется модальное окно с формой
            self.click(OPEN_LOGIN_BUTTON)

        with allure.step(f"Вводим логин: {login}"):
            self.fill(LOGIN_INPUT, login)

        with allure.step("Вводим пароль"):
            self.fill(PASSWORD_INPUT, password)

        with allure.step("Нажимаем кнопку входа"):
            # После клика происходит ререндер DOM, URL остаётся https://365sms.com/
            self.click(SUBMIT_BUTTON)

        return HomePage(self.page)