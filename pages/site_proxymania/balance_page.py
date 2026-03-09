"""
Страница баланса proxymania.su.

Выбирает способ пополнения, вводит сумму и редиректит
на внешний домен провайдера Heleket.
"""

import allure

from pages.base_page import BasePage
from pages.site_proxymania.provider_options_page import ProviderOptionsPage

# Выпадающий список выбора способа пополнения на странице баланса
PAYMENT_METHOD_DROPDOWN = "//b[@role='presentation']"

# Вариант способа пополнения Crypto в списке способов оплаты
PAYMENT_METHOD_OPTION = "//li[text()='Crypto (BTC, ETH, LTC, TON, TRX, USDT)']"

# Поле ввода суммы пополнения
AMOUNT_INPUT = "//input[@id='paySum']"

# Сумма пополнения для перехода к платёжной форме провайдера
DEPOSIT_AMOUNT = "1000"

# Кнопка продолжения — запускает редирект на внешний домен heleket
CONTINUE_BUTTON = "//button[@id='placeOrder']"


class BalancePage(BasePage):

    def select_payment_method(self) -> "BalancePage":
        """Открывает выпадающий список и выбирает способ пополнения."""
        with allure.step("Выбираем способ пополнения Crypto"):
            self.click(PAYMENT_METHOD_DROPDOWN)
            # После клика по опции выбранный способ подставляется в форму пополнения
            self.click(PAYMENT_METHOD_OPTION)
        return self

    def fill_amount(self) -> "BalancePage":
        """Вводит сумму пополнения и возвращает себя для цепочки вызовов."""
        with allure.step(f"Вводим сумму пополнения {DEPOSIT_AMOUNT}"):
            self.fill(AMOUNT_INPUT, DEPOSIT_AMOUNT)
        return self

    def continue_to_payment(self) -> "ProviderOptionsPage":
        """Подтверждает сумму и возвращает страницу провайдера с выбором валюты/сети."""
        with allure.step("Нажимаем кнопку продолжения и ждём редирект на провайдера"):
            # После клика происходит полная перезагрузка страницы —
            # редирект на внешний домен https://new-pay.heleket.com/...
            self.click(CONTINUE_BUTTON)
        return ProviderOptionsPage(self.page)
