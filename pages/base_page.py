from typing import Optional, Callable

from playwright.sync_api import Page, Response


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

    def click_and_capture_response(self, selector: str, predicate: Callable) -> Response:
        """
        Кликает на элемент и перехватывает ответ API удовлетворяющий условию.
        Используется когда клик вызывает API запрос который нужно сохранить для проверки.
        predicate — функция принимающая response и возвращающая True/False.
        Возвращает перехваченный response.
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


    def get_text(self, selector: str) -> Optional[str]:
        """
        Возвращает текстовое содержимое первого найденного элемента по селектору.
        Используется когда нужные данные находятся внутри текста элемента, а не в атрибуте.
        """
        return self.page.locator(selector).text_content()

    def get_attribute(self, selector: str, attribute: str) -> Optional[str]:
        """
        Возвращает значение атрибута элемента по XPath или CSS селектору.
        Используется когда нужные данные хранятся в атрибуте элемента, а не в тексте.
        """
        return self.page.locator(selector).get_attribute(attribute)
