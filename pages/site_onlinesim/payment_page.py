import allure
from pages.base_page import BasePage

# Радиокнопка выбора оплаты криптовалютой — доступна на странице /v2/payment/
CRYPTO_BUTTON = "//label[.//input[@value='cryptocurrency']]"

# Кнопка выбора суммы $50 — после клика происходит редирект на форму провайдера
AMOUNT_50_BUTTON = "//button[text()='$50']"

# Логотип провайдера на форме оплаты — ссылка на сайт exnode.io
PROVIDER_LOGO = "//a[@href='https://exnode.io/']"

# Элемент с адресом кошелька — адрес находится в текстовом содержимом div
WALLET_ADDRESS_CONTAINER = "//div[starts-with(text(),'T') and string-length(text())>30]"


class PaymentPage(BasePage):

    def select_crypto(self) -> "PaymentPage":
        """Выбирает способ оплаты Cryptocurrency и возвращает себя для цепочки"""
        with allure.step("Выбираем способ оплаты: Crypto"):
            # После клика активируется блок выбора суммы пополнения
            self.click(CRYPTO_BUTTON)
        return self

    def select_amount_50(self) -> "PaymentPage":
        """Выбирает сумму $50 и переходит на форму платёжного провайдера"""
        with allure.step("Выбираем сумму пополнения: $50"):
            # После клика происходит редирект на форму провайдера
            self.click(AMOUNT_50_BUTTON)
        return self

    def is_payment_integration_present(self) -> bool:
        """Проверяет наличие логотипа Exnode на форме оплаты"""
        with allure.step("Проверяем наличие логотипа Exnode"):
            return self.is_first_visible(PROVIDER_LOGO)

    def attach_wallet_address(self) -> None:
        """Извлекает адрес кошелька из текста элемента и прикрепляет к allure репорту"""
        with allure.step("Извлекаем адрес кошелька"):
            wallet_address = self.get_text(WALLET_ADDRESS_CONTAINER)

        with allure.step(f"Адрес кошелька: {wallet_address}"):
            allure.attach(
                wallet_address or "Адрес не найден",
                name="Адрес кошелька",
                attachment_type=allure.attachment_type.TEXT
            )
