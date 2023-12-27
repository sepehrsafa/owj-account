import uuid
from typing import Annotated, Union

from app.models import UserAccount as UserAccountModel
from app.models import Wallet as WalletModel
from app.models import WalletTransaction as WalletTransactionModel
from app.models.business import BusinessAccount as BusinessAccountModel
from app.schemas import (
    WalletTransactionFilter,
    WalletTransactionRequestByBusinessID,
    WalletTransactionRequestByUserID,
    WalletTransactionResponse,
    WalletTransactionsResponse,
)
from app.services.auth.utils import check_user_set, get_current_active_user
from app.services.wallet import wallet_topoff
from fastapi import APIRouter, Depends, HTTPException, Path, Security
from pydantic import ValidationError
from tortoise.transactions import in_transaction

from owjcommon.dependencies import get_trace_id, pagination
from owjcommon.enums import CurrencyChoices, UserPermission, UserSet, UserTypeChoices
from owjcommon.exceptions import OWJException, OWJPermissionException
from owjcommon.logger import TraceLogger
from owjcommon.models import get_paginated_results_with_filter
from owjcommon.response import responses
from owjcommon.schemas import Response

logger = TraceLogger(__name__)

router = APIRouter(
    tags=["Wallet Transaction"],
)


# create wallet transaction
@router.post("", response_model=WalletTransactionResponse)
async def create_wallet_transaction(
    wallet_transaction_request: Union[
        WalletTransactionRequestByUserID, WalletTransactionRequestByBusinessID
    ],
    current_user: Annotated = Security(
        get_current_active_user, scopes=[UserPermission.WALLET_TRANSACTION_CREATE]
    ),
    trace_id=Depends(get_trace_id),
):
    """
    Type and Scope:

    - **Type**: AGENCY User Set
    - **Scope**: WALLET_TRANSACTION:CREATE
    """
    check_user_set(current_user, UserSet.AGENCY)
    logger.debug("Creating wallet transaction", trace_id)
    wallet_transaction = None
    async with in_transaction():
        if isinstance(wallet_transaction_request, WalletTransactionRequestByUserID):
            wallet = (
                await WalletModel.filter(
                    user_id=wallet_transaction_request.user_id,
                    currency=wallet_transaction_request.currency,
                )
                .select_for_update()
                .first()
            )
        else:
            wallet = (
                await WalletModel.filter(
                    business_id=wallet_transaction_request.business_id,
                    currency=wallet_transaction_request.currency,
                )
                .select_for_update()
                .first()
            )

        if wallet is None:
            raise OWJException("E1000")

        wallet_transaction = await WalletTransactionModel.create(
            wallet=wallet,
            amount=wallet_transaction_request.amount,
            currency=wallet_transaction_request.currency,
            preformed_by=current_user,
            note=wallet_transaction_request.note,
            reference=wallet_transaction_request.reference,
            balance=wallet.amount + wallet_transaction_request.amount,
        )
        wallet.amount = wallet.amount + wallet_transaction_request.amount
        await wallet.save()

    if wallet_transaction:
        return WalletTransactionResponse(data=wallet_transaction)
    else:
        raise OWJException("E1000")


# all transactions
@router.get("", response_model=WalletTransactionsResponse)
async def get_wallet_transactions(
    current_user: Annotated = Security(
        get_current_active_user, scopes=[UserPermission.WALLET_TRANSACTION_READ]
    ),
    trace_id=Depends(get_trace_id),
    pagination=Depends(pagination),
    filters: WalletTransactionFilter = Depends(),
):
    """
    Type and Scope:

    - **Type**: AGENCY User Set
    - **Scope**: WALLET_TRANSACTION:READ
    """
    check_user_set(current_user, UserSet.AGENCY)
    logger.debug("Getting wallet transactions", trace_id)

    transactions = await get_paginated_results_with_filter(
        WalletTransactionModel,
        pagination["offset"],
        pagination["size"],
        user_filters=filters.dict(exclude_none=True),
    )

    return transactions


# get my wallet transactions
@router.get("/me", response_model=WalletTransactionsResponse)
async def get_my_wallet_transactions(
    current_user: Annotated = Security(
        get_current_active_user,
    ),
    trace_id=Depends(get_trace_id),
    pagination=Depends(pagination),
    filters: WalletTransactionFilter = Depends(),
):
    """
    Type and Scope:

    - **Type**: Any User Set
    - **Scope**: None
    """
    logger.debug(f"Getting my wallet transactions {current_user}", trace_id)

    if current_user.type in UserSet.BUSINESS.value:
        transactions = await get_paginated_results_with_filter(
            WalletTransactionModel,
            pagination["offset"],
            pagination["size"],
            user_filters=filters.dict(exclude_none=True),
            system_filters={"wallet__business_id": current_user.business_id},
        )
    else:
        transactions = await get_paginated_results_with_filter(
            WalletTransactionModel,
            pagination["offset"],
            pagination["size"],
            user_filters=filters.dict(exclude_none=True),
            system_filters={"wallet__user_id": current_user.id},
        )
    return transactions


@router.get("/me/{id}", response_model=WalletTransactionResponse)
async def get_my_wallet_transaction(
    id: int = Path(
        ...,
        description="Transaction UUID",
        example=1,
    ),
    current_user: Annotated = Security(get_current_active_user),
    trace_id=Depends(get_trace_id),
):
    """
    Type and Scope:

    - **Type**: Any User Set
    - **Scope**: None
    """
    logger.debug(f"Getting my wallet transaction with uuid {uuid}", trace_id)
    if current_user.type in UserSet.BUSINESS.value:
        transaction = await WalletTransactionModel.get_or_exception(
            id=id, wallet__business_id=current_user.business_id
        )
    else:
        transaction = await WalletTransactionModel.get_or_exception(
            id=id, wallet__user_id=current_user.id
        )
    return WalletTransactionResponse(data=transaction)


# get business wallet transactions
@router.get("/business/{business_id}", response_model=WalletTransactionsResponse)
async def get_business_wallet_transactions(
    business_id: int = Path(..., description="Business ID", example=1),
    current_user: Annotated = Security(
        get_current_active_user, scopes=[UserPermission.WALLET_TRANSACTION_READ]
    ),
    trace_id=Depends(get_trace_id),
    pagination=Depends(pagination),
    filters: WalletTransactionFilter = Depends(),
):
    """
    Type and Scope:

    - **Type**: AGENCY or Business User Set
    - **Scope**: WALLET_TRANSACTION:READ
    """
    check_user_set(current_user, UserSet.AGENCY_AND_BUSINESS)
    logger.debug(f"Getting business wallet transactions {business_id}", trace_id)

    if current_user.type in UserSet.BUSINESS.value and current_user.id != business_id:
        raise OWJPermissionException()

    return await get_paginated_results_with_filter(
        WalletTransactionModel,
        pagination["offset"],
        pagination["size"],
        user_filters=filters.dict(exclude_none=True),
        system_filters={"wallet__business_id": business_id},
    )


# get user wallet transactions
@router.get("/{user_id}", response_model=WalletTransactionsResponse)
async def get_user_wallet_transactions(
    user_id: int = Path(..., description="User ID", example=1),
    current_user: Annotated = Security(
        get_current_active_user, scopes=[UserPermission.WALLET_TRANSACTION_READ]
    ),
    trace_id=Depends(get_trace_id),
    pagination=Depends(pagination),
    filters: WalletTransactionFilter = Depends(),
):
    """
    Type and Scope:

    - **Type**: Any User Set
    - **Scope**: None
    """
    logger.debug(f"Getting user wallet transactions {user_id}", trace_id)

    # get user
    user_account = await UserAccountModel.get_or_exception(id=user_id)

    if (
        current_user.type in UserSet.REGULAR.value
        and user_account.id != current_user.id
    ):
        raise OWJPermissionException()

    if (
        current_user.type in UserSet.BUSINESS.value
        and current_user.business_id != user_account.business_id
    ):
        raise OWJPermissionException()

    if user_account.type in UserSet.BUSINESS.value:
        transactions = await get_paginated_results_with_filter(
            WalletTransactionModel,
            pagination["offset"],
            pagination["size"],
            user_filters=filters.dict(exclude_none=True),
            system_filters={"wallet__business_id": user_account.business_id},
        )

    else:
        transactions = await get_paginated_results_with_filter(
            WalletTransactionModel,
            pagination["offset"],
            pagination["size"],
            user_filters=filters.dict(exclude_none=True),
            system_filters={"wallet__user_id": user_account.id},
        )

    return transactions
