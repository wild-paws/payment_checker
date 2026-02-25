import allure
from pages.base_page import BasePage
from pages.site_starzspins.home_page import HomePage

# Стартовая страница с сразу открытой модалкой входа
URL = "https://www.starzspins.com/?modal=login"

# Поле ввода логина или email в модальном окне входа
LOGIN_INPUT = "//input[@aria-label='Username or email']"

# Поле ввода пароля в модальном окне входа
PASSWORD_INPUT = "//input[@aria-label='Password']"

# Кнопка подтверждения входа в модальном окне
SUBMIT_BUTTON = "//button[@data-testid='login-submit-btn']"


class LoginPage(BasePage):

    def open(self) -> "LoginPage":
        """Открывает страницу с модальным окном входа и возвращает себя для цепочки"""
        with allure.step("Открываем сайт Starzspins с формой входа"):
            # Модалка входа открывается сразу через параметр ?modal=login
            self.goto(URL)
        return self

    def login(self, login: str, password: str) -> "HomePage":
        """Заполняет форму входа и возвращает главную страницу после авторизации"""
        with allure.step(f"Вводим логин: {login}"):
            self.fill(LOGIN_INPUT, login)

        with allure.step("Вводим пароль"):
            self.fill(PASSWORD_INPUT, password)

        with allure.step("Нажимаем кнопку входа"):
            # После клика происходит ререндер DOM, URL меняется на https://www.starzspins.com/
            self.click(SUBMIT_BUTTON)

        return HomePage(self.page)
