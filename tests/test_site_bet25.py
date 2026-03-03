import allure
import pytest

from pages.site_bet25 import BASE_URL
from pages.site_bet25.login_page import LoginPage
from config.settings import settings
from tests.base_test import BaseTest


# Тест-пример паттерна 3 — закомментируй строку ниже чтобы запустить
# @pytest.mark.skip(reason="Пример паттерна — не запускать")
@pytest.mark.clear_session(BASE_URL)
@allure.feature(BASE_URL)
@allure.story("Проверка адреса кошелька USDT")
class TestBet25(BaseTest):

    @allure.title("Проверка адреса кошелька USDT на совпадение с известными")
    @allure.description(
        "Авторизуемся на bet25.com, переходим в депозит, выбираем USDT, "
        "сохраняем адрес кошелька и проверяем его совпадение с известными адресами "
        "из known_wallets в credentials.json")
    def test_payment_integration(self):
        deposit_page = (
            LoginPage(self.page)
            .open()
            .click_sign_in()
            .login(self.credentials["login"], self.credentials["password"])
            .go_to_deposit()
            .select_usdt()
        )

        deposit_page.attach_wallet_address()

        assert deposit_page.is_payment_integration_present(settings.KNOWN_WALLETS), \
            "Адрес кошелька не совпал ни с одним из известных адресов в known_wallets (credentials.json)"
