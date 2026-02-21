import allure
from tests.base_test import BaseTest
from pages.site_starzspins.login_page import LoginPage


@allure.feature("Starzspins.com")
@allure.story("Платёжная интеграция Praxis")
class TestStarzspins(BaseTest):

    @allure.title("Проверка наличия провайдера Praxis в ответе API")
    @allure.description(
        "Авторизуемся на starzspins.com, открываем страницу депозита и проверяем наличие провайдера Praxis в ответе API")
    def test_payment_integration(self):
        wallet_page = (
            LoginPage(self.page)
            .open()
            .login(self.credentials["login"], self.credentials["password"])
        )

        assert wallet_page.is_payment_integration_present(), \
            "Провайдер Praxis не найден в ответе API"
