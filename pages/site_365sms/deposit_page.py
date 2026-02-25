import allure
from pages.base_page import BasePage
from pages.site_365sms.payment_page import PaymentPage

# Кнопка выбора способа оплаты Crypto
CRYPTO_BUTTON = "//button/span[contains(text(),'CRYPTO')]"

# Кнопка выбора валюты USDT в сети TRC20 — появляется после выбора Crypto
USDT_BUTTON = "//button/span[contains(text(),'USDT (TRC20)')]"

# Кнопка выбора суммы 300₽ — после клика происходит редирект на платёжную форму
AMOUNT_BUTTON = "//button/span[contains(text(),'300₽')]"


class DepositPage(BasePage):

    def select_crypto(self) -> "DepositPage":
        """Выбирает способ оплаты Crypto и возвращает себя для цепочки"""
        with allure.step("Выбираем способ оплаты: Crypto"):
            # После клика появляются доступные криптовалюты
            self.click(CRYPTO_BUTTON)
        return self

    def select_usdt_trc20(self) -> "DepositPage":
        """Выбирает валюту USDT TRC20 и возвращает себя для цепочки"""
        with allure.step("Выбираем валюту: USDT (TRC20)"):
            # После выбора валюты появляются доступные суммы
            self.click(USDT_BUTTON)
        return self

    def confirm_amount(self) -> "PaymentPage":
        """Выбирает сумму 300₽ и возвращает страницу формы оплаты провайдера"""
        with allure.step("Выбираем сумму 300₽"):
            # После клика происходит полная перезагрузка страницы —
            # редирект на внешний домен https://new-pay.heleket.com/...
            self.click(AMOUNT_BUTTON)
        return PaymentPage(self.page)