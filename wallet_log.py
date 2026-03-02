import json
import os
from typing import Optional

# Файл живёт в корне проекта — не в reports/, та папка чистится перед каждым запуском
WALLET_LOG_FILE = os.path.join(os.path.dirname(__file__), "wallets_report.json")

# Сессионный буфер — накапливает данные текущего прогона до записи в файл
# Ключ: nodeid теста, значение: {site, wallets}
_buffer: dict[str, dict] = {}

# nodeid теста который выполняется прямо сейчас — устанавливается фикстурой в conftest
_current_node_id: Optional[str] = None


def set_current_test(node_id: str) -> None:
    """Устанавливает контекст текущего теста. Вызывается из conftest фикстуры."""
    global _current_node_id
    _current_node_id = node_id


def record(site: str, wallet: Optional[str]) -> None:
    """
    Записывает адрес кошелька для текущего теста.
    Вызывается из attach_wallet_address() каждого page object.
    site — домен сайта, например "365sms.com".
    wallet — адрес кошелька, может быть None если элемент не нашёлся.
    """
    if not _current_node_id:
        return

    if _current_node_id not in _buffer:
        _buffer[_current_node_id] = {"site": site, "wallets": []}

    # Сохраняем сайт даже если кошелёк None — нужно для удаления при успехе теста
    _buffer[_current_node_id]["site"] = site

    if wallet and wallet not in _buffer[_current_node_id]["wallets"]:
        _buffer[_current_node_id]["wallets"].append(wallet)


def process_result(node_id: str, passed: bool) -> None:
    """
    Обновляет файл wallets_report.json по результату теста.
    Вызывается из pytest_runtest_makereport в conftest.

    Если тест прошёл — удаляет сайт из файла (проблема устранена).
    Если тест упал и есть кошельки — добавляет их в файл без дублей.
    Если тест упал но кошелёк не был захвачен — файл не трогает
    (это инфраструктурная ошибка, а не проблема кошелька).
    """
    if node_id not in _buffer:
        return

    entry = _buffer[node_id]
    site = entry["site"]
    wallets = entry["wallets"]

    data = _load()

    if passed:
        # Тест прошёл — сайт больше не проблемный, убираем из отчёта
        data.pop(site, None)
    elif wallets:
        # Тест упал и кошелёк был захвачен — добавляем новые адреса без дублей
        if site not in data:
            data[site] = []
        for wallet in wallets:
            if wallet not in data[site]:
                data[site].append(wallet)

    _save(data)


def _load() -> dict:
    """Загружает текущий файл отчёта. Возвращает пустой dict если файла нет."""
    if os.path.exists(WALLET_LOG_FILE):
        with open(WALLET_LOG_FILE, encoding="utf-8") as f:
            return json.load(f)
    return {}


def _save(data: dict) -> None:
    """Записывает данные в файл. Если данных нет — удаляет файл."""
    if data:
        with open(WALLET_LOG_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    elif os.path.exists(WALLET_LOG_FILE):
        # Все тесты прошли — файл больше не нужен
        os.remove(WALLET_LOG_FILE)
