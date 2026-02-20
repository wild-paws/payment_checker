import pytest


class BaseTest:
    """
    Базовый класс для всех тестов.
    Автоматически инжектирует page и credentials через conftest.py
    """

    @pytest.fixture(autouse=True)
    def setup(self, page, credentials):
        """Инициализирует page и credentials для каждого теста"""
        self.page = page
        self.credentials = credentials
