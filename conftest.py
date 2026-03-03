import os
import shutil
import time
from urllib.parse import urlparse

import allure
import pytest
from patchright.sync_api import sync_playwright
from config.settings import settings
import wallet_log

# Фиксированный профиль браузера — живёт между запусками тестов.
# Накапливает историю, куки и кеш — сайты не режут соединение как у бота.
# Папка добавлена в .gitignore и не коммитится в репозиторий.
BROWSER_PROFILE_DIR = os.path.join(os.path.dirname(__file__), "browser_profile")


@pytest.fixture(scope="session", autouse=True)
def clean_reports():
    """
    Управляет папками с отчётами перед запуском тестов.
    Выполняется автоматически один раз за сессию.

    reports/allure — удаляем файлы старше 30 дней, история накапливается между запусками.
    reports/videos — полностью очищаем перед каждым прогоном (видео при падении
                     уже аттачатся напрямую в allure, папка нужна только как временный буфер).
    """
    now = time.time()

    # Allure — удаляем только устаревшее, история за 30 дней остаётся
    os.makedirs("reports/allure", exist_ok=True)
    for filename in os.listdir("reports/allure"):
        filepath = os.path.join("reports/allure", filename)
        if os.path.isfile(filepath) and now - os.path.getmtime(filepath) > 30 * 24 * 3600:
            os.remove(filepath)

    # Videos — полная очистка, файлы уже сохранены в allure аттачментах
    shutil.rmtree("reports/videos", ignore_errors=True)
    os.makedirs("reports/videos")

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
def page(playwright_instance):
    """
    Создаёт persistent context и страницу для каждого теста.

    Persistent context — полноценный браузерный профиль, не инкогнито.
    Использует фиксированный профиль browser_profile/ — сайты не режут соединение
    по fingerprint, так как браузер выглядит как обычный пользователь с историей.

    Трейс отключён — patchright несовместим с context.tracing.start().
    CDP команды трейсинга детектируются сайтами и вызывают ERR_CONNECTION_CLOSED.
    При падении доступно только видео из allure репорта.

    При падении хук pytest_runtest_makereport сохраняет видео в allure.
    При успехе — просто закрывает контекст без сохранения артефактов.
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

    try:
        context.close()
    except Exception:
        # Контекст уже закрыт хуком pytest_runtest_makereport при падении теста
        pass


@pytest.fixture(scope="function", autouse=True)
def clear_session(page, request):
    """
    Чистит сессию перед тестом согласно выбранной стратегии.
    Выполняется автоматически для каждого теста — но только если навешен маркер.
    Без маркера ничего не делает.

    URL передаётся чтобы открыть сайт и получить доступ к его хранилищам.
    Куки всегда чистятся только по домену из URL — глобальная очистка
    ломает профиль и вызывает капчу на чувствительных сайтах.

    Стратегии:
      cookies — только куки (дефолт)
                достаточно в большинстве случаев
      full    — куки + localStorage + sessionStorage + IndexedDB
                используй если сайт помнит сессию даже после очистки куков

    Использование:
      @pytest.mark.clear_session(SITE_URL)                      # cookies (дефолт)
      @pytest.mark.clear_session(SITE_URL, strategy="full")     # куки + все хранилища
    """
    marker = request.node.get_closest_marker("clear_session")
    if not marker:
        yield
        return

    url = marker.args[0]
    strategy = marker.kwargs.get("strategy", "cookies")
    domain = urlparse(url).netloc  # например: starzspins.com, bet25.com

    # Открываем сайт чтобы получить доступ к его хранилищам
    page.goto(url)

    # Чистим куки только конкретного домена — глобальная очистка ломает профиль
    for d in [domain, f".{domain}"]:
        page.context.clear_cookies(domain=d)

    if strategy == "full":
        # Чистим все хранилища включая IndexedDB —
        # некоторые сайты хранят сессию именно там, а не в куках
        page.evaluate("""
            localStorage.clear();
            sessionStorage.clear();
            indexedDB.databases().then(dbs => {
                dbs.forEach(db => indexedDB.deleteDatabase(db.name));
            });
        """)

    yield


@pytest.fixture(scope="function", autouse=True)
def track_wallet(request):
    """
    Устанавливает контекст текущего теста для wallet_log и сбрасывает его после.
    Позволяет page object'ам вызывать wallet_log.record() без передачи item напрямую.
    """
    wallet_log.set_current_test(request.node.nodeid)
    yield
    wallet_log.clear_current_test()


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    Хук pytest — выполняется после каждой фазы теста (setup, call, teardown).
    При падении фазы call сохраняет видео в allure репорт.
    tryfirst=True — запускаем раньше других хуков, чтобы успеть закрыть контекст.
    hookwrapper=True — оборачивает выполнение хука, yield отдаёт управление pytest.
    """
    outcome = yield
    rep = outcome.get_result()
    setattr(item, f"rep_{rep.when}", rep)

    # Реагируем только на завершение основной фазы теста, не setup/teardown
    if rep.when == "call" and "page" in item.funcargs:

        # Обновляем файл кошельков по результату теста
        wallet_log.process_result(item.nodeid, passed=not rep.failed)

        # При падении сохраняем видео в allure
        if rep.failed:
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


@pytest.fixture(scope="function")
def credentials(request):
    """
    Возвращает словарь с кредами для текущего теста.

    Читает SITE_URL из модуля теста и ищет домен в credentials.json.
    Если домен не найден — возвращает запись "default".
    Нормализация URL происходит в settings.get_credentials() — можно писать
    URL в любом формате, www. и trailing slash учитываются автоматически.

    Если SITE_URL не задан в модуле — использует запись "default" напрямую,
    минуя нормализацию домена.
    """
    site_url = getattr(request.module, "SITE_URL", None)
    if site_url is None:
        # SITE_URL не задан в модуле — используем default напрямую,
        # минуя нормализацию чтобы не полагаться на случайное совпадение строки "default"
        return settings.get_credentials("default")
    return settings.get_credentials(site_url)
