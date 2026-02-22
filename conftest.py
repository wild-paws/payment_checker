import os
import shutil

import allure
import pytest
from playwright.sync_api import sync_playwright
from config.settings import settings


@pytest.fixture(scope="session", autouse=True)
def clean_reports():
    """
    Очищает и пересоздаёт папки с отчётами перед запуском тестов.
    Выполняется автоматически один раз за сессию.
    Папки: reports/allure — данные для allure репорта,
           reports/videos — записи экранов при падении,
           reports/traces — трейсы playwright при падении.
    """
    for folder in ["reports/allure", "reports/videos", "reports/traces"]:
        shutil.rmtree(folder, ignore_errors=True)
        os.makedirs(folder, exist_ok=True)
    yield


@pytest.fixture(scope="session")
def browser():
    """
    Запускает Chromium один раз на всю сессию тестов.
    Настройки берутся из .env файла через config/settings.py:
    HEADLESS — запускать ли браузер без окна (true/false),
    SLOW_MO — задержка между действиями в мс (удобно для отладки).
    """
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
    """
    Создаёт новый контекст браузера и вкладку для каждого теста.
    Контекст изолирован — куки, сессии и localStorage не шарятся между тестами.
    Записывает видео и трейс во время теста.
    При падении хук pytest_runtest_makereport сохраняет оба артефакта в allure.
    При успехе — просто закрывает контекст без сохранения артефактов.
    """
    context = browser.new_context(
        record_video_dir="reports/videos",
        record_video_size={"width": 1280, "height": 720}
    )
    # screenshots=True — скриншот при каждом действии, snapshots=True — снапшот DOM
    context.tracing.start(screenshots=True, snapshots=True)
    page = context.new_page()

    yield page

    # Контекст мог быть уже закрыт хуком при падении теста — просто игнорируем
    try:
        context.tracing.stop()
        context.close()
    except Exception:
        pass


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    Хук pytest — выполняется после каждой фазы теста (setup, call, teardown).
    При падении фазы call сохраняет трейс и видео в allure репорт.
    tryfirst=True — запускаем раньше других хуков, чтобы успеть закрыть контекст.
    hookwrapper=True — оборачивает выполнение хука, yield отдаёт управление pytest.
    """
    # yield передаёт управление pytest — после него тест уже выполнен
    outcome = yield
    # rep содержит результат фазы: статус (passed/failed), исключение если было
    rep = outcome.get_result()
    # Сохраняем результат фазы в атрибут item — фикстура page читает его как request.node.rep_call
    setattr(item, f"rep_{rep.when}", rep)

    # Реагируем только на падение основной фазы теста, не setup/teardown
    if rep.when == "call" and rep.failed and "page" in item.funcargs:
        page = item.funcargs["page"]
        context = page.context

        # Останавливаем трейс ПЕРЕД закрытием контекста — иначе файл не запишется
        trace_path = f"reports/traces/{item.name}.zip"
        try:
            context.tracing.stop(path=trace_path)
            allure.attach.file(
                trace_path,
                name="trace",
                attachment_type=allure.attachment_type.ZIP
            )
        except Exception:
            pass

        # Берём путь до закрытия контекста — video объект доступен пока контекст жив
        video_path = page.video.path()
        # Закрываем контекст — только после этого Playwright записывает файл на диск
        context.close()

        try:
            with open(video_path, "rb") as f:
                allure.attach(
                    f.read(),
                    name="video",
                    attachment_type=allure.attachment_type.WEBM
                )
        except Exception:
            pass


@pytest.fixture(scope="session")
def credentials():
    """
    Возвращает словарь с кредами из .env файла.
    Используется во всех тестах через BaseTest.setup.
    Значения задаются в .env: LOGIN и PASSWORD.
    """
    return {
        "login": settings.LOGIN,
        "password": settings.PASSWORD,
    }
