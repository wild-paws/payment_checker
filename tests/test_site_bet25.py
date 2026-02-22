import allure
import pytest

from tests.base_test import BaseTest
from pages.site_bet25.login_page import LoginPage
from config.settings import settings


# Тест-пример паттерна 3 — закомментируй строку ниже чтобы запустить
@pytest.mark.skip(reason="Пример паттерна — не запускать")
@allure.feature("bet25.com")
@allure.story("Проверка адреса кошелька USDT")
class TestBet25(BaseTest):

    @allure.title("Проверка адреса кошелька USDT на совпадение с известными")
    @allure.description(
        "Авторизуемся на bet25.com, переходим в депозит, выбираем USDT, "
        "сохраняем адрес кошелька и проверяем его совпадение с известными адресами из .env")
    def test_payment_integration(self):
        payment_page = (
            LoginPage(self.page)
            .open()
            .click_sign_in()
            .login(self.credentials["login"], self.credentials["password"])
            .go_to_deposit()
            .select_usdt()
        )

        payment_page.attach_wallet_address()

        assert payment_page.is_payment_integration_present(settings.KNOWN_WALLETS), \
            "Адрес кошелька не совпал ни с одним из известных адресов в KNOWN_WALLETS"
