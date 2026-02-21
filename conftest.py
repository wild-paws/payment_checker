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
    При падении — сохраняет видео и трейс в allure репорт.
    При успехе — просто закрывает контекст без сохранения артефактов.
    """
    # Создаём контекст с записью видео
    context = browser.new_context(
        record_video_dir="reports/videos",
        record_video_size={"width": 1280, "height": 720}
    )
    # Запускаем трейс — записывает скриншоты и снапшоты DOM
    context.tracing.start(screenshots=True, snapshots=True)
    page = context.new_page()

    yield page

    # Проверяем упал ли тест — rep_call устанавливается хуком pytest_runtest_makereport
    failed = request.node.rep_call.failed if hasattr(request.node, "rep_call") else False

    if failed:
        trace_path = f"reports/traces/{request.node.name}.zip"
        try:
            # Останавливаем трейс и сохраняем в zip архив
            context.tracing.stop(path=trace_path)
            # Прикрепляем трейс к allure репорту
            allure.attach.file(
                trace_path,
                name="trace",
                attachment_type=allure.attachment_type.ZIP
            )
        except Exception:
            # Контекст мог быть уже закрыт хуком pytest_runtest_makereport
            pass
        finally:
            context.close()
    else:
        context.tracing.stop()
        context.close()


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    Хук pytest — выполняется после каждой фазы теста (setup, call, teardown).
    Сохраняет результат фазы в атрибут item чтобы фикстура page могла его прочитать.
    При падении фазы call — берёт путь к видео, закрывает контекст
    (это гарантирует запись файла на диск) и прикрепляет видео к allure репорту.
    """
    outcome = yield
    rep = outcome.get_result()
    # Сохраняем результат фазы — доступен как request.node.rep_call в фикстурах
    setattr(item, f"rep_{rep.when}", rep)

    if rep.when == "call" and rep.failed and "page" in item.funcargs:
        page = item.funcargs["page"]
        # Берём путь до того как закрыть контекст
        video_path = page.video.path()
        # Закрываем контекст — playwright записывает файл на диск только после закрытия
        page.context.close()
        # Прикрепляем видео к allure репорту
        with open(video_path, "rb") as f:
            allure.attach(
                f.read(),
                name="video",
                attachment_type=allure.attachment_type.WEBM
            )


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