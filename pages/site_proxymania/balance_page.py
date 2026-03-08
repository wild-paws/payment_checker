"""
Страница баланса proxymania.su.

Выбирает способ пополнения, вводит сумму и редиректит
на внешнюю платёжную форму провайдера.
"""

import allure

from pages.base_page import BasePage
from pages.site_proxymania.payment_page import PaymentPage

# Выпадающий список выбора способа пополнения на странице баланса
PAYMENT_METHOD_DROPDOWN = "//span[@id='select2-payMethod-container']"

# Вариант способа пополнения (ID из текущей DOM-разметки сайта)
PAYMENT_METHOD_OPTION = "//li[@id='select2-payMethod-result-bsoy-15']"

# Поле ввода суммы пополнения
AMOUNT_INPUT = "//input[@id='paySum']"

# Сумма пополнения для перехода к платёжной форме провайдера
DEPOSIT_AMOUNT = "1000"

# Кнопка продолжения — запускает редирект на внешний домен heleket
CONTINUE_BUTTON = "//button[@id='placeOrder']"


class BalancePage(BasePage):

    def select_payment_method(self) -> "BalancePage":
        """Открывает выпадающий список и выбирает способ пополнения."""
        with allure.step("Выбираем способ пополнения"):
            self.click(PAYMENT_METHOD_DROPDOWN)
            # После клика по опции выбранный способ подставляется в форму
            self.click(PAYMENT_METHOD_OPTION)
        return self

    def fill_amount(self) -> "BalancePage":
        """Вводит сумму пополнения и возвращает себя для цепочки вызовов."""
        with allure.step(f"Вводим сумму пополнения {DEPOSIT_AMOUNT}"):
            self.fill(AMOUNT_INPUT, DEPOSIT_AMOUNT)
        return self

    def continue_to_payment(self) -> "PaymentPage":
        """Подтверждает сумму и возвращает страницу платёжной формы провайдера."""
        with allure.step("Нажимаем кнопку продолжения и ждём редирект на провайдера"):
            # После клика происходит полная перезагрузка страницы —
            # редирект на внешний домен https://new-pay.heleket.com/...
            with self.page.expect_navigation():
                self.click(CONTINUE_BUTTON)
        return PaymentPage(self.page)
