import allure
from playwright.sync_api import Page
from pages.base_page import BasePage
from pages.site_starzspins.wallet_page import WalletPage

# URL страницы с модалкой логина — открывается сразу с формой входа через query параметр
# Это позволяет пропустить клик на кнопку входа и сразу заполнять форму
URL = "https://www.starzspins.com/?modal=login"

# Поле ввода логина или email в модальном окне входа
LOGIN_INPUT = "//input[@aria-label='Username or email']"

# Поле ввода пароля в модальном окне входа
PASSWORD_INPUT = "//input[@aria-label='Password']"

# Кнопка подтверждения входа в модальном окне
SUBMIT_BUTTON = "//button[@data-testid='login-submit-btn']"


class LoginPage(BasePage):

    def open(self) -> "LoginPage":
        """Открывает страницу сразу с модалкой логина и возвращает себя для цепочки"""
        with allure.step("Открываем сайт Starzspins с формой входа"):
            # Открываем URL сразу с модалкой — не нужно искать кнопку входа на странице
            self.goto(URL)
        return self

    def login(self, login: str, password: str) -> "WalletPage":
        """Заполняет форму входа и возвращает страницу кошелька после авторизации"""
        with allure.step(f"Вводим логин: {login}"):
            self.fill(LOGIN_INPUT, login)

        with allure.step("Вводим пароль"):
            self.fill(PASSWORD_INPUT, password)

        with allure.step("Нажимаем кнопку входа"):
            # После клика SPA авторизует пользователя без смены URL
            self.click(SUBMIT_BUTTON)

        with allure.step("Ожидаем закрытия формы входа"):
            # Ждём пока кнопка входа исчезнет — это сигнал, что авторизация прошла
            # и можно переходить к следующему шагу
            self.wait_for_selector(SUBMIT_BUTTON, state="hidden")

        # open() вызывается здесь, а не в тесте — он перехватывает API ответ при переходе на страницу депозита
        # если вызвать open() позже, API запрос уже уйдёт и ответ будет пропущен
        return WalletPage(self.page).open()
