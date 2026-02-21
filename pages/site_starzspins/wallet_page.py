import allure
from playwright.sync_api import Page
from pages.base_page import BasePage

URL = "https://www.starzspins.com/?modal=wallet&tab=deposit"
PROVIDERS_API = "/api/deposit/get_providers"
PROVIDER_NAME = "Praxis"


class WalletPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)

    def is_payment_integration_present(self) -> bool:
        with allure.step("Открываем страницу депозита и перехватываем список провайдеров"):
            response = self.goto(URL, lambda r: PROVIDERS_API in r.url)

        with allure.step(f"Проверяем наличие провайдера {PROVIDER_NAME} в ответе API"):
            providers = [p["code"] for p in response.json().get("data", [])]
            allure.attach(
                str(providers),
                name="Список провайдеров",
                attachment_type=allure.attachment_type.TEXT
            )
            return PROVIDER_NAME in providers
