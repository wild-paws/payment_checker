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
        page — уже открытая вкладка persistent browser profile (pages[0] контекста),
               создаётся в conftest.py.
        credentials — словарь с логином и паролем из credentials.json.
        pytest автоматически передаёт фикстуры из conftest.py по имени параметра.
        """
        self.page = page
        self.credentials = credentials
