import allure
from playwright.sync_api import Page
from pages.base_page import BasePage

# URL страницы депозита — открывается сразу с нужной вкладкой через query параметры
URL = "https://www.starzspins.com/?modal=wallet&tab=deposit"

# Путь к API который возвращает список доступных платёжных провайдеров
PROVIDERS_API = "/api/deposit/get_providers"

# Название провайдера платёжной интеграции которое ищем в ответе API
PROVIDER_NAME = "Praxis"


class WalletPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)

    def is_payment_integration_present(self) -> bool:
        """
        Открывает страницу депозита, перехватывает ответ API со списком провайдеров
        и проверяет наличие нужного провайдера в списке.
        Возвращает True если провайдер найден, False если нет.
        """
        with allure.step("Открываем страницу депозита и перехватываем список провайдеров"):
            # Переходим на страницу и одновременно ждём ответа от API провайдеров
            # predicate — функция которая проверяет URL каждого ответа
            response = self.goto(URL, lambda r: PROVIDERS_API in r.url)

        with allure.step(f"Проверяем наличие провайдера {PROVIDER_NAME} в ответе API"):
            # Извлекаем список кодов провайдеров из ответа
            # Структура ответа: {"data": [{"code": "Praxis"}, ...]}
            providers = [p["code"] for p in response.json().get("data", [])]

            # Прикрепляем список провайдеров к allure репорту для отладки
            allure.attach(
                str(providers),
                name="Список провайдеров",
                attachment_type=allure.attachment_type.TEXT
            )

            return PROVIDER_NAME in providers