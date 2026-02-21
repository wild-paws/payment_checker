from __future__ import annotations

import allure
from playwright.sync_api import Page
from pages.base_page import BasePage

# Логотип Heleket на платёжной форме — ссылка ведёт на сайт провайдера
# На странице два элемента с этим селектором — берём первый (шапка формы)
HELEKET_LOGO = "//a[@href='https://heleket.com']"


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