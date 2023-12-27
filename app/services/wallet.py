from owjcommon.enums import CurrencyChoices, UserSet
from app.models import Wallet as WalletModel
from app.models.finance import IPG as IPGModel, IPGTransaction as IPGTransactionModel
from app.schemas.finance import WalletTopOffRequest
from app.services.ipg import get_ipg_client
from owjcommon.exceptions import OWJException


async def create_wallets(user_account, business=None):
    for currency in CurrencyChoices:
        wallet = await WalletModel.create(
            user=user_account,
            currency=currency,
            business=business,
        )
        await wallet.save()


async def wallet_topoff(current_user, requested_for_user, request: WalletTopOffRequest):
    ipg = (
        await IPGModel.filter(is_active=True, currency=request.currency)
        .order_by("-priority")
        .first()
    )

    if not ipg:
        raise OWJException("E1024")

    ipg_client = get_ipg_client(ipg.type)

    ipg_client = ipg_client(
        terminal_id=ipg.terminal_id,
        merchant_id=ipg.merchant_id,
        merchant_key=ipg.merchant_key,
        password=ipg.password,
        callback_url=ipg.callback_url,
        url=ipg.url,
        currency=ipg.currency,
    )

    # get client wallet, if client type is business, get business wallet, else get user wallet
    if requested_for_user.type in UserSet.BUSINESS.value:
        wallet = await WalletModel.get_or_exception(
            business_id=requested_for_user.business_id, currency=request.currency
        )
    else:
        wallet = await WalletModel.get_or_exception(
            user=requested_for_user, currency=request.currency
        )

    ipg_transaction = await IPGTransactionModel.create(
        user=current_user,
        ipg=ipg,
        type="topoff",
        amount=request.amount,
        currency=request.currency,
        note=request.note,
        reference=request.reference,
        wallet=wallet,
    )

    transaction = ipg_client.pay(
        amount=request.amount,
        currency=request.currency,
        phone_number=current_user.phone_number,
        order_id=ipg_transaction.pk,
        reference=request.reference,
        description=request.note,
    )

    ipg_transaction.token = transaction.token
    await ipg_transaction.save()

    return transaction
