from typing import Annotated

from app.models import UserAccount as UserAccountModel
from app.models.business import BusinessAccount as BusinessAccountModel
from app.models import Wallet as WalletModel
from app.schemas import (
    WalletResponse,
    WalletsResponse,
    WalletTopOffRequest,
    WalletTopOffResponse,
    WalletUpdate,
)
from app.services.auth.utils import check_user_set, get_current_active_user
from app.services.wallet import wallet_topoff
from fastapi import APIRouter, Depends, Path, Security

from owjcommon.dependencies import get_trace_id
from owjcommon.enums import CurrencyChoices, UserPermission, UserSet
from owjcommon.exceptions import OWJException, OWJPermissionException
from owjcommon.logger import TraceLogger
from owjcommon.response import responses
from owjcommon.schemas import Response

logger = TraceLogger(__name__)

router = APIRouter(
    tags=["Wallet"],
)


# get my wallet
@router.get(
    "/me",
    response_model=WalletsResponse,
    responses=responses,
)
async def get_my_wallets(
    current_user: Annotated = Security(get_current_active_user),
    trace_id=Depends(get_trace_id),
):
    """
    Type and Scope:

    - **Type**: Any User Set
    - **Scope**: None
    """
    logger.debug(f"Getting my wallets {current_user}", trace_id)
    if current_user.type in UserSet.BUSINESS.value:
        wallets = await WalletModel.filter(business_id=current_user.business_id).all()
    else:
        wallets = await WalletModel.filter(user=current_user).all()
    return WalletsResponse(items=wallets)


# get my wallet based on currency
@router.get(
    "/me/{currency}",
    response_model=WalletResponse,
    responses=responses,
)
async def get_my_wallet(
    currency: CurrencyChoices = Path(
        ..., description="Currency", example=CurrencyChoices.IRR
    ),
    current_user: Annotated = Security(get_current_active_user),
    trace_id=Depends(get_trace_id),
):
    """
    Type and Scope:

    - **Type**: Any User Set
    - **Scope**: None
    """
    logger.debug(f"Getting my wallet with currency {currency}", trace_id)
    if current_user.type in UserSet.BUSINESS.value:
        wallet = await WalletModel.get_or_exception(
            business_id=current_user.business_id, currency=currency
        )
    else:
        wallet = await WalletModel.get_or_exception(
            user=current_user, currency=currency
        )
    return WalletResponse(data=wallet)


@router.post(
    "/me/deposit",
    response_model=WalletTopOffResponse,
    responses=responses,
)
async def topoff_my_wallet(
    request: WalletTopOffRequest,
    current_user: Annotated = Security(get_current_active_user),
    trace_id=Depends(get_trace_id),
):
    """
    Type and Scope:

    - **Type**: Any User Set
    - **Scope**: None
    """
    logger.debug(
        f"Topoff my wallet with currency {request.currency} and request {request.dict()}",
        trace_id,
    )

    return await wallet_topoff(current_user, current_user, request)


# get business wallets
@router.get(
    "/business/{business_id}",
    response_model=WalletsResponse,
    responses=responses,
)
async def get_business_wallets(
    business_id: int = Path(..., description="Business ID", example=1),
    current_user: Annotated = Security(
        get_current_active_user, scopes=[UserPermission.WALLET_READ]
    ),
    trace_id=Depends(get_trace_id),
):
    """
    Type and Scope:

    - **Type**: AGENCY or BUSINESS User Set
    - **Scope**: WALLET_READ
    """
    check_user_set(current_user, UserSet.AGENCY_AND_BUSINESS)
    logger.debug(f"Getting business wallets {business_id}", trace_id)

    business_account = await BusinessAccountModel.get_or_exception(id=business_id)

    if current_user.type in UserSet.BUSINESS.value:
        if business_account.id != current_user.business_id:
            raise OWJPermissionException()
        wallets = await WalletModel.filter(business_id=business_account.id).all()

    else:
        wallets = await WalletModel.filter(business_id=business_account.id).all()

    return WalletsResponse(items=wallets)


# update business wallet
@router.put(
    "/business/{business_id}",
    response_model=WalletResponse,
    responses=responses,
)
async def update_business_wallet(
    data: WalletUpdate,
    business_id: int = Path(..., description="Wallet ID", example=1),
    current_user: Annotated = Security(
        get_current_active_user, scopes=[UserPermission.WALLET_UPDATE]
    ),
    trace_id=Depends(get_trace_id),
):
    """
    Type and Scope:

    - **Type**: AGENCY User Set
    - **Scope**: WALLET:UPDATE
    """
    check_user_set(current_user, UserSet.AGENCY)
    logger.debug(f"Updating wallet {business_id}", trace_id)
    # check user to see if business or user
    wallet = await WalletModel.get_or_exception(
        business_id=business_id, currency=data.currency
    )
    wallet.update_from_dict(data.dict())
    await wallet.save()
    return WalletResponse(data=wallet)


# get user wallets
@router.get(
    "/{user_id}",
    response_model=WalletsResponse,
    responses=responses,
)
async def get_user_wallets(
    user_id: int = Path(..., description="User ID", example=1),
    current_user: Annotated = Security(
        get_current_active_user, scopes=[UserPermission.WALLET_READ]
    ),
    trace_id=Depends(get_trace_id),
):
    """
    Type and Scope:

    - **Type**: AGENCY or BUSINESS User Set
    - **Scope**: WALLET_READ
    """
    check_user_set(current_user, UserSet.AGENCY_AND_BUSINESS)
    logger.debug(f"Getting user wallets {user_id}", trace_id)

    user_account = await UserAccountModel.get_or_exception(id=user_id)

    if (
        current_user.type in UserSet.BUSINESS.value
        and user_account.business_id != current_user.business_id
    ):
        raise OWJPermissionException()

    if user_account.type in UserSet.BUSINESS.value:
        wallets = await WalletModel.filter(business_id=user_account.business_id).all()

    else:
        wallets = await WalletModel.filter(user=user_id).all()

    return WalletsResponse(items=wallets)


# update wallet
@router.put(
    "/{user_id}",
    response_model=WalletResponse,
    responses=responses,
)
async def update_wallet(
    data: WalletUpdate,
    user_id: int = Path(..., description="Wallet ID", example=1),
    current_user: Annotated = Security(
        get_current_active_user, scopes=[UserPermission.WALLET_UPDATE]
    ),
    trace_id=Depends(get_trace_id),
):
    """
    Type and Scope:

    - **Type**: AGENCY User Set
    - **Scope**: WALLET:UPDATE
    """
    check_user_set(current_user, UserSet.AGENCY)
    logger.debug(f"Updating wallet {user_id}", trace_id)
    # check user to see if business or user
    user_account = await UserAccountModel.get_or_exception(id=user_id)
    if user_account.type in UserSet.BUSINESS.value:
        wallet = await WalletModel.get_or_exception(
            business_id=user_account.business_id, currency=data.currency
        )
    else:
        wallet = await WalletModel.get_or_exception(
            user=user_id, currency=data.currency
        )
    wallet.update_from_dict(data.dict())
    await wallet.save()
    return WalletResponse(data=wallet)


@router.get(
    "/{user_id}/{currency}",
    response_model=WalletResponse,
    responses=responses,
)
async def get_user_wallet(
    currency: CurrencyChoices = Path(
        ..., description="Currency", example=CurrencyChoices.IRR
    ),
    user_id: int = Path(..., description="User ID", example=1),
    current_user: Annotated = Security(
        get_current_active_user, scopes=[UserPermission.WALLET_READ]
    ),
    trace_id=Depends(get_trace_id),
):
    """
    Type and Scope:

    - **Type**: AGENCY or BUSINESS User Set
    - **Scope**: WALLET:READ
    """
    check_user_set(current_user, UserSet.AGENCY_AND_BUSINESS)
    logger.debug(f"Getting user wallets {user_id}", trace_id)

    user_account = await UserAccountModel.get_or_exception(id=user_id)

    if current_user.type in UserSet.BUSINESS.value:
        if user_account.business_id != current_user.business_id:
            raise OWJPermissionException()
        wallets = await WalletModel.get_or_exception(
            business_id=user_account.business_id, currency=currency
        )

    else:
        wallets = await WalletModel.get_or_exception(user=user_id, currency=currency)

    return WalletResponse(data=wallets)


@router.post(
    "/{user_id}/deposit",
    response_model=WalletTopOffResponse,
    responses=responses,
)
async def topoff_user_wallet(
    request: WalletTopOffRequest,
    user_id: int = Path(
        ..., description="The User ID you want to deposit money for.", example=1
    ),
    current_user: Annotated = Security(get_current_active_user),
    trace_id=Depends(get_trace_id),
):
    """
    Type and Scope:

    - **Type**: Any
    - **Scope**: None
    """
    requested_for_user = await UserAccountModel.get_or_exception(id=user_id)
    return await wallet_topoff(current_user, requested_for_user, request)
