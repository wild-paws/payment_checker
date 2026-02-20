from playwright.sync_api import Page


class BasePage:
    def __init__(self, page: Page):
        self.page = page

    def goto(self, url: str, predicate=None):
        """Переходит на URL. Если передан предикат — ждёт matching ответа и возвращает его"""
        if predicate:
            with self.page.expect_response(predicate) as response_info:
                self.page.goto(url)
            return response_info.value
        else:
            self.page.goto(url)
            return None

    def fill(self, selector: str, value: str):
        """Вводит текст в поле по селектору"""
        self.page.fill(selector, value)

    def click(self, selector: str):
        """Кликает на элемент по селектору"""
        self.page.click(selector)

    def click_and_wait_for_navigation(self, selector: str):
        """Кликает на элемент и ждёт редиректа"""
        with self.page.expect_navigation():
            self.click(selector)

    def wait_for_selector(self, selector: str, state: str = "visible"):
        """Ждёт появления элемента в указанном состоянии"""
        self.page.wait_for_selector(selector, state=state)

    def is_first_visible(self, selector: str) -> bool:
        """Возвращает True если первый из найденных элементов виден на странице"""
        return self.page.locator(selector).first.is_visible()