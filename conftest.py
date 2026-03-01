import os
import shutil
from urllib.parse import urlparse

import allure
import pytest
from patchright.sync_api import sync_playwright
from config.settings import settings

# Фиксированный профиль браузера — живёт между запусками тестов.
# В отличие от временного профиля, накапливает историю, куки и кеш —
# сайты видят "живой" профиль и не режут соединение как у бота.
# Папка добавлена в .gitignore и не коммитится в репозиторий.
BROWSER_PROFILE_DIR = os.path.join(os.path.dirname(__file__), "browser_profile")


@pytest.fixture(scope="session", autouse=True)
def clean_reports():
    """
    Очищает и пересоздаёт папки с отчётами перед запуском тестов.
    Выполняется автоматически один раз за сессию.
    Папки: reports/allure — данные для allure репорта,
           reports/videos — записи экранов при падении.
    Трейс отключён — patchright несовместим с context.tracing.start():
    CDP команды трейсинга детектируются некоторыми сайтами и вызывают
    ERR_CONNECTION_CLOSED ещё до загрузки страницы.
    """
    for folder in ["reports/allure", "reports/videos"]:
        shutil.rmtree(folder, ignore_errors=True)  # ignore_errors — папки может не быть при первом запуске
        os.makedirs(folder, exist_ok=True)
    yield


@pytest.fixture(scope="session")
def playwright_instance():
    """
    Запускает Playwright один раз на всю сессию тестов.
    Отдельная фикстура нужна потому что при launch_persistent_context
    browser-объекта нет — контекст является точкой входа напрямую.
    """
    settings.validate()
    with sync_playwright() as p:
        yield p


@pytest.fixture(scope="function")
def page(playwright_instance, request):
    """
    Создаёт persistent context и страницу для каждого теста.
    Persistent context — полноценный браузерный профиль, не инкогнито.
    Это ключевое отличие от new_context(): сайты не режут соединение
    по fingerprint, так как браузер выглядит как обычный пользователь.

    Использует фиксированный профиль browser_profile/ вместо временного —
    сайты не детектируют бота по пустому профилю без истории и куков.

    Записывает видео во время теста.
    При падении хук pytest_runtest_makereport сохраняет видео в allure.
    При успехе — просто закрывает контекст без сохранения артефактов.
    Трейс отключён из-за несовместимости patchright с context.tracing.start().
    """
    os.makedirs(BROWSER_PROFILE_DIR, exist_ok=True)

    context = playwright_instance.chromium.launch_persistent_context(
        user_data_dir=BROWSER_PROFILE_DIR,
        headless=settings.HEADLESS,
        slow_mo=settings.SLOW_MO,
        viewport={"width": 1280, "height": 720},
        record_video_dir="reports/videos",
        record_video_size={"width": 1280, "height": 720},
    )

    # pages[0] — уже открытая вкладка от persistent context.
    # new_page() открыла бы вторую лишнюю вкладку поверх неё.
    page = context.pages[0]

    yield page

    # Контекст мог быть уже закрыт хуком при падении теста — просто игнорируем
    try:
        context.close()
    except Exception:
        pass


@pytest.fixture(scope="function", autouse=True)
def clear_session(page, request):
    """
    Чистит сессию перед тестом.
    Выполняется автоматически для каждого теста — но только если навешен маркер.
    Без маркера ничего не делает.

    URL передаётся чтобы открыть сайт и получить доступ к его хранилищам.
    Куки чистятся только по домену из URL — глобальная очистка ломает профиль
    и вызывает капчу на сайтах которые проверяют историю браузера.

    По умолчанию чистит только куки.
    Добавь strategy="full" если сайт помнит сессию даже после очистки куков:
      @pytest.mark.clear_session("https://site.com")
      @pytest.mark.clear_session("https://site.com", strategy="full")
    """
    marker = request.node.get_closest_marker("clear_session")
    if not marker:
        yield
        return

    url = marker.args[0]
    domain = urlparse(url).netloc

    # Открываем сайт чтобы получить доступ к его хранилищам
    page.goto(url)

    # Чистим куки только конкретного домена — глобальная очистка ломает профиль
    # и вызывает капчу на сайтах которые проверяют историю браузера.
    # Чистим оба варианта: с точкой (.site.com) и без (site.com) —
    # разные сайты ставят куки по-разному
    for d in [domain, f".{domain}"]:
        page.context.clear_cookies(domain=d)

    if marker.kwargs.get("strategy") == "full":
        # Чистим все хранилища включая IndexedDB —
        # некоторые сайты хранят сессию именно там а не в куках
        page.evaluate("""
            localStorage.clear();
            sessionStorage.clear();
            indexedDB.databases().then(dbs => {
                dbs.forEach(db => indexedDB.deleteDatabase(db.name));
            });
        """)

    yield


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    Хук pytest — выполняется после каждой фазы теста (setup, call, teardown).
    При падении фазы call сохраняет видео в allure репорт.
    tryfirst=True — запускаем раньше других хуков, чтобы успеть закрыть контекст.
    hookwrapper=True — оборачивает выполнение хука, yield отдаёт управление pytest.
    Трейс отключён из-за несовместимости patchright с context.tracing.start().
    """
    # yield передаёт управление pytest — после него тест уже выполнен
    outcome = yield
    # rep содержит результат фазы: статус (passed/failed), исключение если было
    rep = outcome.get_result()
    # Сохраняем результат фазы в атрибут item
    setattr(item, f"rep_{rep.when}", rep)

    # Реагируем только на падение основной фазы теста, не setup/teardown
    if rep.when == "call" and rep.failed and "page" in item.funcargs:
        page = item.funcargs["page"]
        context = page.context

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
            pass  # не даём упасть хуку если артефакт не удалось сохранить


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
