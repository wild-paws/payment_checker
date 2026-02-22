import allure
from playwright.sync_api import Page
from pages.base_page import BasePage

# Логотип Heleket на платёжной форме — ссылка ведёт на сайт провайдера
# На странице два элемента с этим селектором — берём первый (шапка формы)
HELEKET_LOGO = "//a[@href='https://heleket.com']"

# Контейнер с адресом кошелька — адрес хранится в атрибуте title этого div
WALLET_ADDRESS_CONTAINER = "//p[text()='Адрес кошелька для перевода:']/following-sibling::div"


class HeleketPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)

    def is_payment_integration_present(self) -> bool:
        """Ждёт загрузки страницы и проверяет наличие логотипа Heleket"""
        with allure.step("Ожидаем загрузки платёжной формы Heleket"):
            # Ждём появления логотипа — страница Heleket грузится после редиректа
            # без явного ожидания тест падает так как элемент ещё не в DOM
            self.wait_for_selector(HELEKET_LOGO)

        with allure.step("Проверяем наличие логотипа Heleket на странице"):
            # is_first_visible берёт первый из двух найденных элементов
            return self.is_first_visible(HELEKET_LOGO)

    def attach_wallet_address(self) -> None:
        """Извлекает адрес кошелька из атрибута title и прикрепляет к allure репорту"""
        with allure.step("Извлекаем адрес кошелька для перевода"):
            # Адрес хранится в атрибуте title div-контейнера под заголовком
            wallet_address = self.get_attribute(WALLET_ADDRESS_CONTAINER, "title")

        with allure.step(f"Адрес кошелька: {wallet_address}"):
            allure.attach(
                wallet_address or "Адрес не найден",
                name="Адрес кошелька",
                attachment_type=allure.attachment_type.TEXT
            )