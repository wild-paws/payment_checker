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

# ВАЖНО: pytest должен запускаться из корня проекта.
# Папки reports/ создаются относительно рабочей директории.
# Если запустить из другой директории — reports/ окажется не в корне проекта.


@pytest.fixture(scope="session", autouse=True)
def clean_reports():
    """
    Управляет папками с отчётами перед запуском тестов.
    Выполняется автоматически один раз за сессию.

    reports/allure — удаляем файлы и папки старше 30 дней,
                     история накапливается между запусками.
    reports/videos — полностью очищаем перед каждым прогоном (видео при падении
                     уже аттачатся напрямую в allure, папка нужна только как временный буфер).
    """
    now = time.time()

    # Allure — удаляем только устаревшее (файлы и папки), история за 30 дней остаётся.
    # Allure создаёт подпапки (history/, widgets/ и т.д.) — чистим их тоже.
    os.makedirs("reports/allure", exist_ok=True)
    for entry in os.listdir("reports/allure"):
        entry_path = os.path.join("reports/allure", entry)
        if now - os.path.getmtime(entry_path) > 30 * 24 * 3600:
            if os.path.isfile(entry_path):
                os.remove(entry_path)
            elif os.path.isdir(entry_path):
                shutil.rmtree(entry_path)

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
    # Fallback на new_page() на случай если pages почему-то пустой.
    page = context.pages[0] if context.pages else context.new_page()

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
    Куки чистятся по домену из URL — глобальная очистка ломает профиль
    и вызывает капчу на чувствительных сайтах.

    Для www-доменов чистятся куки и корневого домена тоже —
    иначе куки установленные на .site.com не затрагиваются.

    Стратегии:
      cookies — только куки (дефолт)
                достаточно в большинстве случаев
      full    — куки + localStorage + sessionStorage + IndexedDB
                используй если сайт помнит сессию даже после очистки куков

    Использование:
      @pytest.mark.clear_session(BASE_URL)                      # cookies (дефолт)
      @pytest.mark.clear_session(BASE_URL, strategy="full")     # куки + все хранилища
    """
    marker = request.node.get_closest_marker("clear_session")
    if not marker:
        yield
        return

    url = marker.args[0]
    strategy = marker.kwargs.get("strategy", "cookies")
    domain = urlparse(url).netloc  # например: www.starzspins.com, bet25.com
    root_domain = domain.removeprefix("www.")  # starzspins.com — корневой домен без www.

    # Открываем сайт чтобы получить доступ к его хранилищам
    page.goto(url)

    # Чистим куки по домену и корневому домену.
    # Для www-доменов без этого куки на .site.com остались бы нетронутыми.
    domains_to_clear = [domain, f".{domain}"]
    if root_domain != domain:
        domains_to_clear += [root_domain, f".{root_domain}"]

    for d in domains_to_clear:
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


@pytest.hookimpl(tryfirst=True, wrapper=True)
def pytest_runtest_makereport(item, call):  # noqa: ARG001 — call требуется сигнатурой хука pytest
    """
    Хук pytest — выполняется после каждой фазы теста (setup, call, teardown).
    При падении фазы call сохраняет видео в allure репорт.
    tryfirst=True — запускаем раньше других хуков, чтобы успеть закрыть контекст.
    wrapper=True  — современный синтаксис обёртки (hookwrapper deprecated в pytest 8+).
    """
    rep = yield

    setattr(item, f"rep_{rep.when}", rep)

    # Реагируем только на завершение основной фазы теста, не setup/teardown
    if rep.when == "call" and "page" in item.funcargs:

        # Обновляем файл кошельков по результату теста
        wallet_log.process_result(item.nodeid, passed=not rep.failed)

        # При падении сохраняем видео в allure
        if rep.failed:
            page = item.funcargs["page"]
            context = page.context

            # Берём путь до закрытия контекста — video объект доступен пока контекст жив.
            # page.video может быть None если видеозапись не инициализировалась.
            video_path = None
            try:
                video_path = page.video.path()
            except Exception:
                pass

            # Закрываем контекст — только после этого Playwright записывает файл на диск
            context.close()

            if video_path:
                try:
                    with open(video_path, "rb") as f:
                        allure.attach(
                            f.read(),
                            name="video",
                            attachment_type=allure.attachment_type.WEBM
                        )
                except Exception:
                    pass  # не даём упасть хуку если артефакт не удалось сохранить

    return rep


@pytest.fixture(scope="function")
def credentials(request):
    """
    Возвращает словарь с кредами для текущего теста.

    Читает BASE_URL из модуля теста и ищет домен в credentials.json.
    BASE_URL импортируется в тест из __init__.py пакета сайта —
    единственного места где определяется домен.

    Если домен не найден в credentials.json — возвращает запись "default".
    Нормализация URL происходит в settings.get_credentials() — www. и trailing slash
    учитываются автоматически.

    Если BASE_URL не задан в модуле — использует запись "default" напрямую,
    минуя нормализацию домена.
    """
    base_url = getattr(request.module, "BASE_URL", None)
    if base_url is None:
        # BASE_URL не задан в модуле — используем default напрямую,
        # минуя нормализацию чтобы не полагаться на случайное совпадение строки "default"
        return settings.get_credentials("default")
    return settings.get_credentials(base_url)
