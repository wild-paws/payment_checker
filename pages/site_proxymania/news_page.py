"""
Страница новостей proxymania.su после авторизации.

Содержит переход на страницу баланса пользователя.
"""

import allure

from pages.base_page import BasePage
from pages.site_proxymania.balance_page import BalancePage

# Вторая кнопка "Баланс" в интерфейсе — ведёт на страницу /balance/
BALANCE_BUTTON = "(//a[@href='/balance/'])[2]"


class NewsPage(BasePage):

    def go_to_balance(self) -> "BalancePage":
        """Переходит на страницу баланса и возвращает соответствующий page object."""
        with allure.step("Переходим на страницу баланса"):
            # После клика происходит ререндер DOM, URL меняется на /balance/
            self.click(BALANCE_BUTTON)
        return BalancePage(self.page)
