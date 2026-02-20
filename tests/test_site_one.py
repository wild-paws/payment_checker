from tests.base_test import BaseTest
from pages.site_365sms.login_page import LoginPage


class TestSiteOne(BaseTest):
    def test_payment_integration(self):
        """Проверяет наличие логотипа Heleket на платёжной форме сайта 365sms.com"""
        heleket_page = (
            LoginPage(self.page)
            .open()
            .login(self.credentials["login"], self.credentials["password"])
            .navigate_to_payment()
        )

        assert heleket_page.is_payment_integration_present(), \
            "Логотип Heleket не найден на странице оплаты"
