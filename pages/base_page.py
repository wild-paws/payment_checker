from typing import Optional

from playwright.sync_api import Page


class BasePage:
    """
    Базовый класс для всех страниц.
    Содержит общие методы работы с браузером через Playwright.
    Все page объекты наследуются от этого класса.
    Прячет детали реализации Playwright — в наследниках используем только методы этого класса.
    """

    def __init__(self, page: Page):
        # Объект страницы Playwright — основной инструмент взаимодействия с браузером
        self.page = page

    def goto(self, url: str, predicate=None):
        """
        Переходит на указанный URL.
        Если передан predicate — ждёт ответа от сервера удовлетворяющего условию
        и возвращает его. Используется для перехвата API ответов при навигации.
        predicate — функция принимающая response и возвращающая True/False.
        Возвращает response если передан predicate, иначе None.
        """
        if predicate:
            # Оборачиваем goto в expect_response — перехватываем нужный ответ
            # контекстный менеджер гарантирует что не пропустим ответ
            with self.page.expect_response(predicate) as response_info:
                self.page.goto(url)
            return response_info.value
        else:
            self.page.goto(url)
            return None

    def fill(self, selector: str, value: str):
        """
        Вводит текст в поле по XPath или CSS селектору.
        Playwright автоматически ждёт появления элемента перед вводом.
        """
        self.page.fill(selector, value)

    def click(self, selector: str):
        """
        Кликает на элемент по XPath или CSS селектору.
        Playwright автоматически ждёт появления и кликабельности элемента.
        """
        self.page.click(selector)

    def click_and_wait_for_navigation(self, selector: str):
        """
        Кликает на элемент и ждёт завершения навигации на другую страницу.
        Используется когда клик вызывает редирект — на внешний домен или другой URL.
        expect_navigation гарантирует что не продолжим до завершения перехода.
        """
        with self.page.expect_navigation():
            self.click(selector)

    def wait_for_selector(self, selector: str, state: str = "visible"):
        """
        Ждёт появления элемента в указанном состоянии.
        state — состояние элемента:
            visible — элемент виден на странице (по умолчанию),
            hidden — элемент скрыт или удалён из DOM.
        Используется когда Playwright не может автоматически дождаться элемента.
        """
        self.page.wait_for_selector(selector, state=state)

    def is_first_visible(self, selector: str) -> bool:
        """
        Возвращает True если первый из найденных элементов виден на странице.
        Используется когда селектор возвращает несколько элементов —
        берём первый, чтобы избежать ошибки strict mode violation.
        """
        return self.page.locator(selector).first.is_visible()

    def get_attribute(self, selector: str, attribute: str) -> Optional[str]:
        """
        Возвращает значение атрибута элемента по XPath или CSS селектору.
        Используется когда нужные данные хранятся в атрибуте элемента, а не в тексте.
        """
        return self.page.locator(selector).get_attribute(attribute)
