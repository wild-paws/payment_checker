"""
Тест платёжной интеграции Praxis на starzspins.com (паттерн 2 — проверка по API).
"""

import allure
import pytest

from pages.site_starzspins import BASE_URL
from pages.site_starzspins.login_page import LoginPage
from tests.base_test import BaseTest


# Тест-пример паттерна 2 — закомментируй строку ниже чтобы запустить
# @pytest.mark.skip(reason="Пример паттерна — не запускать")
@pytest.mark.clear_session(BASE_URL, strategy="full")
@allure.feature(BASE_URL)
@allure.story("Платёжная интеграция Praxis")
class TestStarzspins(BaseTest):

    @allure.title("Проверка наличия провайдера Praxis в ответе API")
    @allure.description(
        "Авторизуемся на starzspins.com, открываем кошелёк, выбираем USDT TRC-20, "
        "подтверждаем сумму, проверяем наличие провайдера Praxis в ответе API "
        "и сохраняем адрес кошелька"
    )
    def test_payment_integration(self):
        payment_page = (
            LoginPage(self.page)
            .open()
            .login(self.credentials["login"], self.credentials["password"])
            .open_wallet()
            .select_usdt_trc20()
            .confirm_amount()
        )

        payment_page.attach_wallet_address()

        assert payment_page.is_payment_integration_present(), \
            "Провайдер Praxis не найден в ответе API"
