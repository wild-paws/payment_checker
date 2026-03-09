"""
Тест платёжной интеграции Heleket на proxymania.su (паттерн 1 — проверка по логотипу).
"""

import allure
import pytest

from pages.site_proxymania import BASE_URL
from pages.site_proxymania.login_page import LoginPage
from tests.base_test import BaseTest


@pytest.mark.clear_session(BASE_URL)
@allure.feature(BASE_URL)
@allure.story("Платёжная интеграция Heleket")
class TestProxymania(BaseTest):

    @allure.title("Проверка наличия логотипа Heleket на платёжной форме")
    @allure.description(
        "Авторизуемся на proxymania.su, переходим на страницу баланса, выбираем способ "
        "пополнения и сумму, после редиректа на heleket выбираем USDT и TRON (TRC-20), "
        "переходим к оплате, проверяем логотип провайдера и сохраняем адрес кошелька"
    )
    def test_payment_integration(self) -> None:
        payment_page = (
            LoginPage(self.page)
            .open()
            .login(self.credentials["login"], self.credentials["password"])
            .go_to_balance()
            .select_payment_method()
            .fill_amount()
            .continue_to_payment()
            .select_usdt()
            .select_tron_network()
            .proceed_to_payment()
        )

        payment_page.attach_wallet_address()

        assert payment_page.is_payment_integration_present(), \
            "Логотип Heleket не найден на странице оплаты"
