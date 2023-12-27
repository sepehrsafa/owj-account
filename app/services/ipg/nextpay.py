from .client import Client
from owjcommon.enums import CurrencyChoices
import requests
from app.schemas import WalletTopOffResponse
from app.models import IPGTransaction as IPGTransactionModel
from app.enums import TransactionStatus
from decimal import Decimal

class NextPayClient(Client):
    TOKEN_URL = "/nx/gateway/token"
    VERIFY_URL = "/nx/gateway/verify"
    REDIRECT_URL = "/nx/gateway/payment"

    def __init__(
        self,
        terminal_id,
        merchant_id,
        merchant_key,
        password,
        callback_url,
        url,
        currency,
    ):
        super().__init__(
            terminal_id,
            merchant_id,
            merchant_key,
            password,
            callback_url,
            url,
            currency,
        )
        self.headers = {
            "User-Agent": "PostmanRuntime/7.26.8",
            "Content-Type": "application/x-www-form-urlencoded",
        }

    def pay(
        self, amount, currency, phone_number, order_id, reference=None, description=None
    ):
        request_data = {
            "api_key": self.merchant_key,
            "order_id": order_id,
            "amount": amount,
            "callback_uri": self.callback_url,
            "currency": currency,
            "customer_phone": phone_number,
            "custom_json_fields": {
                "description": description,
                "reference": reference,
            },
            "payer_desc": description,
        }

        print(request_data)

        response = requests.post(
            url=self.url + self.TOKEN_URL,
            data=request_data,
            headers=self.headers,
        )

        response = response.json()

        print(response)

        return WalletTopOffResponse(
            type="redirect",
            url=self.url + self.REDIRECT_URL + "/" + response["trans_id"],
            token=response["trans_id"],
        )

    async def verify(self, transaction: IPGTransactionModel):
        request_data = {
            "api_key": self.merchant_key,
            "trans_id": transaction.token,
            "amount": transaction.amount,
            "currency": transaction.currency,
        }

        print(request_data)

        response = requests.post(
            url=self.url + self.VERIFY_URL,
            data=request_data,
            headers=self.headers,
        )

        response = response.json()

        print(response)

        if response["code"] != 0:
            transaction.status = TransactionStatus.FAILED
            transaction.card_number = response["card_holder"]
            transaction.shaparak_reference_id = response["Shaparak_Ref_Id"]
            return

        discrepancy = False

        if Decimal(response["amount"]) != transaction.amount:
            discrepancy = True

        if response["order_id"] != str(transaction.pk):
            discrepancy = True

        if discrepancy:
            transaction.status = TransactionStatus.DISCREPANCY
            return

        transaction.status = TransactionStatus.SUCCESS
        transaction.card_number = response["card_holder"]
        transaction.shaparak_reference_id = response["Shaparak_Ref_Id"]
        return
