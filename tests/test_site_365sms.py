import allure

from pages.site_365sms.login_page import LoginPage
from tests.base_test import BaseTest


@allure.feature("365sms.com")
@allure.story("Платёжная интеграция Heleket")
class Test365sms(BaseTest):

    @allure.title("Проверка наличия логотипа Heleket на платёжной форме")
    @allure.description(
        "Авторизуемся на 365sms.com, переходим к форме оплаты через Crypto → USDT (TRC20) → 300₽ и проверяем наличие логотипа Heleket")
    def test_payment_integration(self):
        heleket_page = (
            LoginPage(self.page)
            .open()
            .login(self.credentials["login"], self.credentials["password"])
            .navigate_to_payment()
        )

        assert heleket_page.is_payment_integration_present(), \
            "Логотип Heleket не найден на странице оплаты"
