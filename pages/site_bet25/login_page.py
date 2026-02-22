import allure
from pages.base_page import BasePage
from pages.site_bet25.home_page import HomePage

# Главная страница сайта — точка входа
URL = "https://bet25.com/"

# Кнопка открытия формы входа в шапке сайта
SIGN_IN_BUTTON = "//a[text()='Login']"

# Поле ввода логина в модальном окне входа
LOGIN_INPUT = "//input[@id='login']"

# Поле ввода пароля в модальном окне входа
PASSWORD_INPUT = "//input[@id='password']"

# Кнопка подтверждения входа в модальном окне
SUBMIT_BUTTON = "//button[@aria-label='sign in']"


class LoginPage(BasePage):

    def open(self) -> "LoginPage":
        """Открывает главную страницу сайта и возвращает себя для цепочки"""
        with allure.step("Открываем сайт bet25.com"):
            self.goto(URL)
        return self

    def click_sign_in(self) -> "LoginPage":
        """Кликает на кнопку входа и открывает модальное окно авторизации"""
        with allure.step("Открываем форму входа"):
            # После клика открывается модалка — URL меняется на /login
            self.click(SIGN_IN_BUTTON)
        return self

    def login(self, login: str, password: str) -> "HomePage":
        """Заполняет форму входа и возвращает главную страницу после авторизации"""
        with allure.step(f"Вводим логин: {login}"):
            self.fill(LOGIN_INPUT, login)

        with allure.step("Вводим пароль"):
            self.fill(PASSWORD_INPUT, password)

        with allure.step("Нажимаем кнопку входа"):
            # После клика страница рендерится, URL возвращается на главную
            self.click(SUBMIT_BUTTON)

        return HomePage(self.page)
