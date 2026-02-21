import os

import allure
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
def page(browser, request):
    """Создаёт новый контекст и вкладку для каждого теста, закрывает после"""
    context = browser.new_context(
        record_video_dir="reports/videos",
        record_video_size={"width": 1280, "height": 720}
    )
    context.tracing.start(screenshots=True, snapshots=True)
    page = context.new_page()

    yield page

    failed = request.node.rep_call.failed if hasattr(request.node, "rep_call") else False

    if failed:
        trace_path = f"reports/traces/{request.node.name}.zip"
        try:
            context.tracing.stop(path=trace_path)
            allure.attach.file(
                trace_path,
                name="trace",
                attachment_type=allure.attachment_type.ZIP
            )
        except Exception:
            pass
        finally:
            context.close()
    else:
        context.tracing.stop()
        context.close()


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Сохраняет результат теста и аттачит видео при падении"""
    outcome = yield
    rep = outcome.get_result()
    setattr(item, f"rep_{rep.when}", rep)

    if rep.when == "call" and rep.failed and "page" in item.funcargs:
        page = item.funcargs["page"]
        video_path = page.video.path()
        page.context.close()
        allure.attach(
            open(video_path, "rb").read(),
            name="video",
            attachment_type=allure.attachment_type.WEBM
        )


@pytest.fixture(scope="session")
def credentials():
    """Возвращает словарь с кредами из .env"""
    return {
        "login": settings.LOGIN,
        "password": settings.PASSWORD,
    }


@pytest.fixture(scope="session", autouse=True)
def clean_reports():
    """Очищает и пересоздаёт папки с отчётами перед запуском тестов"""
    import shutil
    for folder in ["reports/allure", "reports/videos", "reports/traces"]:
        shutil.rmtree(folder, ignore_errors=True)
        os.makedirs(folder, exist_ok=True)
