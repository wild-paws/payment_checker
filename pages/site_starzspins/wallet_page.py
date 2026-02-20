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
        with self.page.expect_response(lambda r: PROVIDERS_API in r.url) as response_info:
            self.page.goto(URL)

        body = response_info.value.json()
        providers = [p["code"] for p in body.get("data", [])]
        return PROVIDER_NAME in providers
