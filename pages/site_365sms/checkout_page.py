import allure
from playwright.sync_api import Page
from pages.base_page import BasePage
from pages.site_365sms.heleket_page import HeleketPage

# Кнопка перехода на страницу пополнения баланса в меню сайта
PAYMENT_BUTTON = "//a[@href='/payments']"

# Кнопка выбора способа оплаты Crypto на странице пополнения
CRYPTO_BUTTON = "//button/span[contains(text(),'CRYPTO')]"

# Кнопка выбора валюты USDT в сети TRC20 — появляется после выбора Crypto
USDT_BUTTON = "//button/span[contains(text(),'USDT (TRC20)')]"

# Кнопка выбора суммы 300₽ — после клика происходит редирект на платёжную форму
AMOUNT_BUTTON = "//button/span[contains(text(),'300₽')]"


class CheckoutPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)

    def navigate_to_payment(self) -> "HeleketPage":
        """Проходит путь до платёжной формы и возвращает страницу Heleket после редиректа"""
        with allure.step("Переходим на страницу пополнения баланса"):
            # Кликаем на кнопку пополнения — SPA загружает страницу без смены URL
            self.click(PAYMENT_BUTTON)

        with allure.step("Выбираем способ оплаты: Crypto"):
            # После клика появляются доступные криптовалюты
            self.click(CRYPTO_BUTTON)

        with allure.step("Выбираем валюту: USDT (TRC20)"):
            # После выбора валюты появляются доступные суммы
            self.click(USDT_BUTTON)

        with allure.step("Выбираем сумму 300₽ и ждём редиректа на платёжную форму"):
            # После выбора суммы происходит редирект на внешний домен heleket.com
            # click_and_wait_for_navigation ждёт завершения редиректа перед продолжением
            self.click_and_wait_for_navigation(AMOUNT_BUTTON)

        return HeleketPage(self.page)
