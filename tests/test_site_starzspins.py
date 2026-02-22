import allure
from tests.base_test import BaseTest
from pages.site_starzspins.login_page import LoginPage


@allure.feature("Starzspins.com")
@allure.story("Платёжная интеграция Praxis")
class TestStarzspins(BaseTest):

    @allure.title("Проверка наличия провайдера Praxis в ответе API")
    @allure.description(
        "Авторизуемся на starzspins.com, открываем кошелёк, выбираем USDT TRC-20, "
        "подтверждаем сумму, проверяем наличие провайдера Praxis в ответе API "
        "и сохраняем адрес кошелька")
    def test_payment_integration(self):
        payment_page = (
            LoginPage(self.page)
            .open()
            .click_sign_in()
            .login(self.credentials["login"], self.credentials["password"])
            .open_wallet()
            .select_usdt_trc20()
            .confirm_amount()
        )

        payment_page.attach_wallet_address()

        assert payment_page.is_payment_integration_present(), \
            "Провайдер Praxis не найден в ответе API"
