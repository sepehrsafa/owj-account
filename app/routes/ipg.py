from time import sleep
from typing import Annotated

from app.enums import IPGType, TransactionStatus
from app.models import IPG as IPGModel
from app.models import IPGTransaction as IPGTransactionModel
from app.models import Wallet as WalletModel
from app.models import WalletTransaction as WalletTransactionModel
from app.schemas import (
    IPGRequest,
    IPGResponse,
    IPGsResponse,
    IPGTransactionResponse,
    IPGTransactionsResponse,
    IPGTransactionFilter,
    IPGUpdateRequest,
    IPGFilter,
)
from app.services.auth.utils import check_user_set, get_current_active_user
from app.services.ipg import get_ipg_client
from fastapi import APIRouter, Depends, HTTPException, Path, Query, Security
from fastapi.responses import RedirectResponse
from tortoise.transactions import in_transaction

from owjcommon.dependencies import get_trace_id, pagination
from owjcommon.enums import UserPermission, UserSet
from owjcommon.exceptions import OWJException
from owjcommon.logger import TraceLogger
from owjcommon.models import get_paginated_results_with_filter
from owjcommon.response import responses
from owjcommon.schemas import Response

logger = TraceLogger(__name__)

router = APIRouter(
    tags=["IPG"],
)


# call back url ?trans_id=8bf6cc9c-2f4f-4520-bd47-5eeb3721dd7d&order_id=6&amount=323232&np_status=Unsuccessful
# get the transaction id and order id and amount and np_status from the url
@router.get("/callback/nextpay")
async def nextpay_callback(
    trans_id: str = Query(
        None,
        description="Transaction ID for NextPay",
        example="8bf6cc9c-2f4f-4520-bd47-5eeb3721dd7d",
    ),
    order_id: str = Query(None, description="Order ID for NextPay", example="6"),
):
    ipg_client = get_ipg_client(IPGType.NEXTPAY)

    async with in_transaction():
        transaction = (
            await IPGTransactionModel.filter(pk=order_id, token=trans_id)
            .select_for_update()
            .first()
        )

        if transaction is None:
            return OWJException("E1025")
        if transaction.status != TransactionStatus.PENDING:
            return OWJException("E1027")

        ipg = await transaction.ipg

        ipg_client = ipg_client(
            terminal_id=ipg.terminal_id,
            merchant_id=ipg.merchant_id,
            merchant_key=ipg.merchant_key,
            password=ipg.password,
            callback_url=ipg.callback_url,
            url=ipg.url,
            currency=ipg.currency,
        )

        await ipg_client.verify(transaction)

        if transaction.status == TransactionStatus.SUCCESS:
            wallet = (
                await WalletModel.filter(id=transaction.wallet_id)
                .select_for_update()
                .first()
            )

            await WalletTransactionModel.create(
                wallet=wallet,
                amount=transaction.amount,
                currency=transaction.currency,
                preformed_by=await transaction.user,
                note=transaction.note,
                reference=transaction.reference_id,
                balance=wallet.amount + transaction.amount,
            )

            wallet.amount = wallet.amount + transaction.amount
            await wallet.save()

        await transaction.save()

    return RedirectResponse(url="https://ptc7.ir", status_code=302)


# get all ipg transactions
@router.get("/transactions", response_model=IPGTransactionsResponse, responses=responses)
async def list_all_ipgs_transactions(
    trace_id=Depends(get_trace_id),
    pagination=Depends(pagination),
    current_user: Annotated = Security(
        get_current_active_user, scopes=[UserPermission.IPG_TRANSACTION_READ]
    ),
    filter: IPGTransactionFilter = Depends(),
):
    check_user_set(current_user, UserSet.AGENCY)
    logger.debug("Listing all ipg transactions", trace_id)
    transactions = await get_paginated_results_with_filter(
        IPGTransactionModel,
        pagination["offset"],
        pagination["size"],
        user_filters=filter.dict(exclude_unset=True),
    )
    return transactions


@router.get("/transactions/{id}", response_model=IPGTransactionResponse, responses=responses)
async def get_ipg_transaction(
    id: int = Path(
        ...,
        description="IPG Transaction ID",
        example=1,
    ),
    trace_id=Depends(get_trace_id),
    current_user: Annotated = Security(
        get_current_active_user, scopes=[UserPermission.IPG_TRANSACTION_READ]
    ),
):
    check_user_set(current_user, UserSet.AGENCY)
    logger.debug(f"Getting ipg transaction with id {id}", trace_id)
    transaction = await IPGTransactionModel.get_or_exception(id=id)
    return {"data": transaction}


# create ipg create, update, delete, list, get
@router.post("", response_model=IPGResponse, responses=responses)
async def create_ipg(
    ipg: IPGRequest,
    current_user: Annotated = Security(
        get_current_active_user, scopes=[UserPermission.IPG_CREATE]
    ),
    trace_id=Depends(get_trace_id),
):
    """
    This Method is for creating a ipg.
    """
    check_user_set(current_user, UserSet.AGENCY)
    logger.debug(f"Creating ipg with request {ipg.dict()}", trace_id)
    ipg = await IPGModel.create(**ipg.dict())
    return IPGResponse(data=ipg)


# list ipgs
@router.get("", response_model=IPGsResponse, responses=responses)
async def list_ipgs(
    trace_id=Depends(get_trace_id),
    pagination=Depends(pagination),
    current_user: Annotated = Security(
        get_current_active_user, scopes=[UserPermission.IPG_READ]
    ),
    filter: IPGFilter = Depends(),
):
    check_user_set(current_user, UserSet.AGENCY)
    logger.debug("Listing ipgs", trace_id)
    ipgs = await get_paginated_results_with_filter(
        IPGModel,
        pagination["offset"],
        pagination["size"],
        user_filters=filter.dict(exclude_unset=True),
    )
    return ipgs


# update ipg
@router.put("/{id}", response_model=IPGResponse, responses=responses)
async def update_ipg(
    request: IPGRequest,
    id: int = Path(..., description="IPG ID", example=1),
    current_user: Annotated = Security(
        get_current_active_user, scopes=[UserPermission.IPG_UPDATE]
    ),
    trace_id=Depends(get_trace_id),
):
    """
    This Method is for updating a ipg.
    """
    check_user_set(current_user, UserSet.AGENCY)
    logger.debug(f"Updating ipg with id {id}", trace_id)
    ipg = await IPGModel.get(pk=id)
    ipg = await ipg.update_from_dict(request.dict(exclude_unset=True))
    await ipg.save(user=current_user)
    return {"data": ipg}


# delete ipg
@router.delete("/{id}", response_model=Response, responses=responses)
async def delete_ipg(
    id: int = Path(..., description="IPG ID", example=1),
    current_user: Annotated = Security(
        get_current_active_user, scopes=[UserPermission.IPG_DELETE]
    ),
    trace_id=Depends(get_trace_id),
):
    """
    This Method is for deleting a ipg.
    """
    check_user_set(current_user, UserSet.AGENCY)
    logger.debug(f"Deleting ipg with id {id}", trace_id)
    ipg = await IPGModel.get(id=id)
    await ipg.delete()
    return Response()


# get ipg
@router.get("/{id}", response_model=IPGResponse, responses=responses)
async def get_ipg(
    id: int = Path(..., description="IPG ID", example=1),
    trace_id=Depends(get_trace_id),
    current_user: Annotated = Security(
        get_current_active_user, scopes=[UserPermission.IPG_READ]
    ),
):
    check_user_set(current_user, UserSet.AGENCY)
    logger.debug(f"Getting ipg with id {id}", trace_id)
    ipg = await IPGModel.get(id=id)
    return IPGResponse(data=ipg)


# list and get ipg transactions
@router.get("/{ipg_id}/transactions", response_model=IPGTransactionsResponse, responses=responses)
async def list_ipg_transactions(
    ipg_id: int = Path(..., description="IPG ID", example=1),
    trace_id=Depends(get_trace_id),
    pagination=Depends(pagination),
    current_user: Annotated = Security(
        get_current_active_user, scopes=[UserPermission.IPG_TRANSACTION_READ]
    ),
    filter: IPGTransactionFilter = Depends(),
):
    check_user_set(current_user, UserSet.AGENCY)
    logger.debug(f"Listing ipg transactions for ipg {ipg_id}", trace_id)
    return await get_paginated_results_with_filter(
        IPGTransactionModel,
        pagination["offset"],
        pagination["size"],
        user_filters=filter.dict(exclude_unset=True),
        system_filters={"ipg_id": ipg_id},
    )
