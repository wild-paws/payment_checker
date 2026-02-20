from playwright.sync_api import Page


class BasePage:
    def __init__(self, page: Page):
        self.page = page

    def open(self, url: str) -> "BasePage":
        """Открывает указанный URL и ждёт полной загрузки страницы"""
        self.page.goto(url)
        return self

    def click_and_wait_for_navigation(self, selector: str):
        """Кликает на элемент и ждёт редиректа"""
        with self.page.expect_navigation():
            self.click(selector)

    def wait_for_load(self):
        """Ждёт пока сеть успокоится (нет активных запросов)"""
        self.page.wait_for_load_state("load")

    def fill(self, selector: str, value: str):
        """Вводит текст в поле по селектору"""
        self.page.fill(selector, value)

    def click(self, selector: str):
        """Кликает на элемент по селектору"""
        self.page.click(selector)

    def is_visible(self, selector: str) -> bool:
        """Возвращает True если элемент виден на странице"""
        return self.page.locator(selector).is_visible()
