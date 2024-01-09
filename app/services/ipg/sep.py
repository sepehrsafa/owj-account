from .client import Client
from owjcommon.enums import CurrencyChoices
import requests
from app.schemas import WalletTopOffResponse
from app.models import IPGTransaction as IPGTransactionModel
from app.enums import TransactionStatus
from decimal import Decimal


class SepClient(Client):
    TOKEN_URL = "/onlinepg/onlinepg"
    VERIFY_URL = "/verifyTxnRandomSessionkey/ipg/VerifyTransaction"
    REDIRECT_URL = "/OnlinePG/SendToken"

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

    def pay(
        self, amount, currency, phone_number, order_id, reference=None, description=None
    ):
        request_data = {
            "action": "token",
            "TerminalId": self.terminal_id,
            "Amount": amount,
            "ResNum": order_id,
            "ResNum1": str(reference),
            "ResNum2": str(description),
            "ResNum3": phone_number,
            "RedirectUrl": self.callback_url,
            "CellNumber": phone_number,
        }
        print(request_data)

        response = requests.post(
            url=self.url + self.TOKEN_URL,
            data=request_data,
        )

        response = response.json()

        return WalletTopOffResponse(
            type="redirect",
            url=self.url + self.REDIRECT_URL + "?token=" + response["token"],
            token=response["token"],
        )

    async def verify(self, transaction: IPGTransactionModel):
        request_data = {
            "RefNum": transaction.ipg_reference_id,
            "TerminalNumber": self.terminal_id,
        }

        response = requests.post(
            url=self.url + self.VERIFY_URL,
            json=request_data,
        )
        print(response.text)

        response = response.json()

        if response["ResultCode"] != 0:
            transaction.status = TransactionStatus.FAILED
            transaction.card_number = response["TransactionDetail"]["MaskedPan"]
            transaction.shaparak_reference_id = response["TransactionDetail"]["RRN"]
            return

        discrepancy = False

        if (
            Decimal(response["TransactionDetail"]["AffectiveAmount"])
            != transaction.amount
        ):
            discrepancy = True

        if discrepancy:
            transaction.status = TransactionStatus.DISCREPANCY
            return

        transaction.status = TransactionStatus.SUCCESS
        transaction.card_number = response["TransactionDetail"]["MaskedPan"]
        transaction.shaparak_reference_id = response["TransactionDetail"]["RRN"]
        return
