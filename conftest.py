import pytest
from playwright.sync_api import sync_playwright
from config.settings import settings


@pytest.fixture(scope="session")
def browser():
    """Запускает Chromium один раз на всю сессию тестов"""
    settings.validate()
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=settings.HEADLESS,
            slow_mo=settings.SLOW_MO,
        )
        yield browser
        browser.close()


@pytest.fixture(scope="function")
def page(browser):
    """Создаёт новый контекст и вкладку для каждого теста, закрывает после"""
    context = browser.new_context()
    page = context.new_page()
    yield page
    context.close()


@pytest.fixture(scope="session")
def credentials():
    """Возвращает словарь с кредами из .env"""
    return {
        "login": settings.LOGIN,
        "password": settings.PASSWORD,
    }
