from tests.base_test import BaseTest
from pages.site_starzspins.login_page import LoginPage


class TestSiteTwo(BaseTest):
    def test_payment_integration(self):
        """Проверяет наличие провайдера Praxis в ответе API на сайте starzspins.com"""
        wallet_page = (
            LoginPage(self.page)
            .open()
            .login(self.credentials["login"], self.credentials["password"])
        )

        assert wallet_page.is_payment_integration_present(), \
            "Провайдер Praxis не найден в ответе API"