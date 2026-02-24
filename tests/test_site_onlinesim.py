import allure

from pages.site_onlinesim.login_page import LoginPage
from tests.base_test import BaseTest


@allure.feature("onlinesim.io")
@allure.story("Платёжная интеграция Exnode")
class TestOnlinesim(BaseTest):

    @allure.title("Проверка наличия логотипа Exnode на платёжной форме")
    @allure.description(
        "Авторизуемся на onlinesim.io, открываем форму пополнения через Top up, "
        "выбираем Crypto и сумму $50, проверяем наличие логотипа Exnode "
        "и сохраняем адрес кошелька")
    def test_payment_integration(self):
        payment_page = (
            LoginPage(self.page)
            .open()
            .login(self.credentials["login"], self.credentials["password"])
            .go_to_payment()
            .select_crypto()
            .select_amount_50()
        )

        payment_page.attach_wallet_address()

        assert payment_page.is_payment_integration_present(), \
            "Логотип Exnode не найден на платёжной форме"
