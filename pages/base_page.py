"""
Базовый класс для всех page object'ов — обёртка над Playwright.

Предоставляет набор методов для навигации, ввода, кликов и чтения атрибутов.
Все страницы наследуются от BasePage и не вызывают self.page.* напрямую,
за исключением frame_locator (iframe) и expect_navigation (редирект на внешний домен).
"""

from typing import Callable

from patchright.sync_api import Page, Response


class BasePage:
    """
    Базовый класс для всех страниц.
    Содержит общие методы работы с браузером через Playwright.
    Все page объекты наследуются от этого класса.
    """

    def __init__(self, page: Page) -> None:
        # Объект страницы Playwright — основной инструмент взаимодействия с браузером
        self.page = page

    def goto(self, url: str) -> None:
        """
        Переходит на указанный URL.
        Используется для открытия начальной страницы перед авторизацией.
        """
        self.page.goto(url)

    def fill(self, selector: str, value: str) -> None:
        """
        Вводит текст в поле по XPath или CSS селектору.
        Playwright автоматически ждёт появления элемента перед вводом.
        """
        self.page.fill(selector, value)

    def click(self, selector: str) -> None:
        """
        Кликает на элемент по XPath или CSS селектору.
        Playwright автоматически ждёт появления и кликабельности элемента.
        """
        self.page.click(selector)

    def click_and_capture_response(
        self,
        selector: str,
        predicate: Callable[[Response], bool],
    ) -> Response:
        """
        Кликает на элемент и перехватывает ответ API удовлетворяющий условию.
        Используется когда клик вызывает API запрос который нужно сохранить для проверки.

        predicate — функция (response: Response) -> bool, возвращает True для нужного ответа.
        Возвращает перехваченный Response.
        """
        # Регистрируем обработчик ДО клика — иначе можем пропустить быстрый ответ
        with self.page.expect_response(predicate) as response_info:
            self.click(selector)
        return response_info.value

    def is_first_visible(self, selector: str) -> bool:
        """
        Возвращает True если первый из найденных элементов виден на странице.
        Используется когда селектор возвращает несколько элементов —
        берём первый, чтобы избежать ошибки strict mode violation.
        """
        return self.page.locator(selector).first.is_visible()

    def get_attribute(self, selector: str, attribute: str) -> str | None:
        """
        Возвращает значение атрибута элемента по XPath или CSS селектору.
        Используется когда нужные данные хранятся в атрибуте элемента, а не в тексте.
        """
        return self.page.locator(selector).get_attribute(attribute)
