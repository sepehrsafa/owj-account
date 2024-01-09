from abc import ABC, abstractmethod
from owjcommon.enums import CurrencyChoices


class Client(ABC):
    def __init__(self, terminal_id, merchant_id, merchant_key, password, callback_url, url, currency):
        self.terminal_id = terminal_id
        self.merchant_id = merchant_id
        self.merchant_key = merchant_key
        self.password = password
        self.callback_url = callback_url
        self.currency = currency
        self.url = url

    @abstractmethod
    def pay(
        self, amount, currency, phone_number, order_id, reference=None, description=None
    ):
        pass

    @abstractmethod
    def verify(self, transaction):
        pass
