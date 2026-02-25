import allure
import pytest

from pages.site_365sms.login_page import LoginPage
from tests.base_test import BaseTest


# Тест-пример паттерна 1 — закомментируй строку ниже чтобы запустить
@pytest.mark.skip(reason="Пример паттерна — не запускать")
@allure.feature("365sms.com")
@allure.story("Платёжная интеграция Heleket")
class Test365sms(BaseTest):

    @allure.title("Проверка наличия логотипа Heleket на платёжной форме")
    @allure.description(
        "Авторизуемся на 365sms.com, переходим на страницу пополнения, "
        "выбираем Crypto → USDT (TRC20) → 300₽, после редиректа на heleket.com "
        "проверяем наличие логотипа провайдера и сохраняем адрес кошелька")
    def test_payment_integration(self):
        payment_page = (
            LoginPage(self.page)
            .open()
            .login(self.credentials["login"], self.credentials["password"])
            .go_to_payments()
            .select_crypto()
            .select_usdt_trc20()
            .confirm_amount()
        )

        payment_page.attach_wallet_address()

        assert payment_page.is_payment_integration_present(), \
            "Логотип Heleket не найден на странице оплаты"
