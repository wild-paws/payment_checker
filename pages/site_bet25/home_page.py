import allure
from pages.base_page import BasePage
from pages.site_bet25.deposit_page import DepositPage

# Кнопка перехода к пополнению депозита в шапке — появляется после авторизации
# Локатор по части href вместо текста кнопки: текст меняется в зависимости от языка интерфейса
# Например: "Deposit" (EN), "Einzahlung" (DE), "Пополнить" (RU)
DEPOSIT_BUTTON = "//a[contains(@href, '/account/cashier/deposit') and contains(@class, 'header-menu__item')]"


class HomePage(BasePage):

    def go_to_deposit(self) -> "DepositPage":
        """Переходит на страницу пополнения депозита и возвращает её"""
        with allure.step("Переходим на страницу пополнения депозита"):
            # После клика URL меняется на https://bet25.com/account/cashier/deposit
            self.click(DEPOSIT_BUTTON)
        return DepositPage(self.page)
