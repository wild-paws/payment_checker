from playwright.sync_api import Page
from pages.base_page import BasePage

URL = "https://www.starzspins.com/?modal=wallet&tab=deposit"
PROVIDERS_API = "/api/deposit/get_providers"
PROVIDER_NAME = "Praxis"


class WalletPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)

    def is_payment_integration_present(self) -> bool:
        """Перехватывает ответ на запрос провайдеров и проверяет наличие Praxis"""
        response = self.goto(URL, lambda r: PROVIDERS_API in r.url)
        providers = [p["code"] for p in response.json().get("data", [])]
        return PROVIDER_NAME in providers