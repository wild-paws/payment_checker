import allure
from pages.base_page import BasePage
from pages.site_starzspins.home_page import HomePage

# Главная страница сайта — точка входа
URL = "https://www.starzspins.com/"

# Кнопка открытия формы входа в шапке сайта
SIGN_IN_BUTTON = "//button[@aria-label='sign_in']"

# Поле ввода логина или email в модальном окне входа
LOGIN_INPUT = "//input[@aria-label='Username or email']"

# Поле ввода пароля в модальном окне входа
PASSWORD_INPUT = "//input[@aria-label='Password']"

# Кнопка подтверждения входа в модальном окне
SUBMIT_BUTTON = "//button[@data-testid='login-submit-btn']"


class LoginPage(BasePage):

    def open(self) -> "LoginPage":
        """Открывает главную страницу сайта и возвращает себя для цепочки"""
        with allure.step("Открываем сайт Starzspins"):
            self.goto(URL)
        return self

    def click_sign_in(self) -> "LoginPage":
        """Кликает на кнопку входа и открывает модальное окно авторизации"""
        with allure.step("Открываем форму входа"):
            # После клика открывается модалка — URL меняется на ?modal=login
            self.click(SIGN_IN_BUTTON)
        return self

    def login(self, login: str, password: str) -> "HomePage":
        """Заполняет форму входа и возвращает главную страницу после авторизации"""
        with allure.step(f"Вводим логин: {login}"):
            self.fill(LOGIN_INPUT, login)

        with allure.step("Вводим пароль"):
            self.fill(PASSWORD_INPUT, password)

        with allure.step("Нажимаем кнопку входа"):
            # После клика SPA авторизует пользователя, URL возвращается на главную
            self.click(SUBMIT_BUTTON)

        return HomePage(self.page)
