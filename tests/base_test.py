import pytest


class BaseTest:
    """
    Базовый класс для всех тестов.
    Автоматически инжектирует page и credentials через фикстуру setup.
    self.page и self.credentials доступны в каждом тесте после инициализации фикстурой.
    """

    @pytest.fixture(autouse=True)
    def setup(self, page, credentials):
        """
        Инициализирует page и credentials для каждого теста.
        page — новая вкладка браузера, создаётся в conftest.py.
        credentials — словарь с логином и паролем из .env файла.
        pytest автоматически передаёт фикстуры из conftest.py по имени параметра.
        """
        self.page = page
        self.credentials = credentials
