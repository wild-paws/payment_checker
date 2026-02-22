import allure
from pages.base_page import BasePage
from pages.site_365sms.payment_page import PaymentPage

# Кнопка перехода на страницу пополнения баланса в меню сайта
PAYMENT_BUTTON = "//a[@href='/payments']"

# Кнопка выбора способа оплаты Crypto на странице пополнения
CRYPTO_BUTTON = "//button/span[contains(text(),'CRYPTO')]"

# Кнопка выбора валюты USDT в сети TRC20 — появляется после выбора Crypto
USDT_BUTTON = "//button/span[contains(text(),'USDT (TRC20)')]"

# Кнопка выбора суммы 300₽ — после клика происходит редирект на платёжную форму
AMOUNT_BUTTON = "//button/span[contains(text(),'300₽')]"


class HomePage(BasePage):

    def go_to_payments(self) -> "HomePage":
        """Переходит на страницу пополнения баланса и возвращает себя для цепочки"""
        with allure.step("Переходим на страницу пополнения баланса"):
            # SPA загружает страницу без смены URL
            self.click(PAYMENT_BUTTON)
        return self

    def select_crypto(self) -> "HomePage":
        """Выбирает способ оплаты Crypto и возвращает себя для цепочки"""
        with allure.step("Выбираем способ оплаты: Crypto"):
            # После клика появляются доступные криптовалюты
            self.click(CRYPTO_BUTTON)
        return self

    def select_usdt_trc20(self) -> "HomePage":
        """Выбирает валюту USDT TRC20 и возвращает себя для цепочки"""
        with allure.step("Выбираем валюту: USDT (TRC20)"):
            # После выбора валюты появляются доступные суммы
            self.click(USDT_BUTTON)
        return self

    def confirm_amount(self) -> "PaymentPage":
        """Выбирает сумму 300₽ и возвращает страницу оплаты после редиректа"""
        with allure.step("Выбираем сумму 300₽ и ждём перехода на платёжную форму"):
            # После клика происходит переход на внешний домен heleket.com
            self.click(AMOUNT_BUTTON)
        return PaymentPage(self.page)
