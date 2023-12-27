from typing import Annotated, Union

from app.models import Wallet as WalletModel
from app.models.business import BusinessAccount as BusinessAccountModel
from app.models.user import UserAccount as UserAccountModel
from app.schemas.business import (
    AgencyBusinessAccountUpdateRequest,
    BusinessAccount,
    BusinessAccountCreateRequest,
    BusinessAccountFilters,
    BusinessAccountResponse,
    BusinessAccountsResponse,
    BusinessAccountUpdateRequest,
)
from app.services.auth.utils import check_user_set, get_current_active_user
from app.services.wallet import create_wallets
from fastapi import APIRouter, Depends, HTTPException, Security

from owjcommon.dependencies import get_trace_id, pagination
from owjcommon.enums import UserPermission, UserSet, UserTypeChoices
from owjcommon.exceptions import OWJException, OWJPermissionException
from owjcommon.models import get_paginated_results_with_filter
from owjcommon.response import responses

router = APIRouter(
    tags=["Business Account"],
)


# create create, update, delete, get, list
@router.post("", response_model=BusinessAccountResponse, responses=responses)
async def create_business_account(
    data: BusinessAccountCreateRequest,
    current_user: UserAccountModel = Security(
        get_current_active_user, scopes=[UserPermission.BUSINESS_ACCOUNT_CREATE]
    ),
):
    """
    Type and Scope:

    - **Type**: AGENCY User Set
    - **Scope**: BUSINESS_ACCOUNT:CREATE

    Description:

    If the provided phone number is already registered as a user, the user will be converted to a business user.
    The users wallets will be assigned to the business.

    If the provided phone number is not registered as a user, a new user will be created and assigned to the business.
    """
    check_user_set(current_user, UserSet.AGENCY)
    try:
        user: UserAccountModel = await UserAccountModel.get_by_identifier(
            data.phone_number
        )

        if user.business_id is not None:
            raise OWJException("E1029")

        # get all the wallets of the user and assign business to them
        business = await BusinessAccountModel.create(name=data.name)
        wallets = await WalletModel.filter(user=user)
        for wallet in wallets:
            wallet.business = business
            await wallet.save()

    except OWJException as e:
        if e.code != "E1002":
            raise e
        user = await UserAccountModel.create(phone_number=data.phone_number)
        business = await BusinessAccountModel.create(name=data.name)
        await create_wallets(user, business=business)

    user.type = UserTypeChoices.BUSINESS_SUPERUSER
    user.business = business
    await user.save()

    return {"data": business}


# me
@router.get(
    "/me",
    response_model=BusinessAccountResponse,
    responses=responses,
    summary="Get the business account of the current user ",
)
async def get_business_account_me(
    current_user: UserAccountModel = Security(get_current_active_user),
):
    """
    Type and Scope:

    - **Type**: BUSINESS User Set
    - **Scope**: None
    """
    check_user_set(current_user, UserSet.BUSINESS)
    business = await BusinessAccountModel.get_or_exception(pk=current_user.business_id)
    return {"data": business}


@router.get("", response_model=BusinessAccountsResponse, responses=responses)
async def list_business_accounts(
    pagination: dict = Depends(pagination),
    filters: BusinessAccountFilters = Depends(),
    current_user: UserAccountModel = Security(
        get_current_active_user, scopes=[UserPermission.BUSINESS_ACCOUNT_READ]
    ),
):
    """
    Type and Scope:

    - **Type**: AGENCY User Set
    - **Scope**: BUSINESS_ACCOUNT:READ
    """
    check_user_set(current_user, UserSet.AGENCY)
    filters = filters.dict(exclude_unset=True)

    return await get_paginated_results_with_filter(
        BusinessAccountModel,
        pagination["offset"],
        pagination["size"],
        user_filters=filters,
    )


@router.get("/{id}", response_model=BusinessAccountResponse, responses=responses)
async def get_business_account(
    id: int,
    current_user: UserAccountModel = Security(
        get_current_active_user, scopes=[UserPermission.BUSINESS_ACCOUNT_READ]
    ),
):
    """
    Type and Scope:

    - **Type**: AGENCY User Set
    - **Scope**: BUSINESS_ACCOUNT:READ
    """
    check_user_set(current_user, UserSet.AGENCY)

    business = await BusinessAccountModel.get_or_exception(pk=id)

    if current_user.type in UserSet.BUSINESS.value:
        if current_user.business_id != business.pk:
            raise OWJPermissionException()

    return {"data": business}


@router.put("/{id}", response_model=BusinessAccountResponse, responses=responses)
async def update_business_account(
    id: int,
    data: Union[AgencyBusinessAccountUpdateRequest, BusinessAccountUpdateRequest],
    current_user: UserAccountModel = Security(
        get_current_active_user,
        scopes=[UserPermission.BUSINESS_ACCOUNT_UPDATE],
    ),
):
    """
    Type and Scope:

    - **Type**: AGENCY_AND_BUSINESS User Set
    - **Scope**: BUSINESS_ACCOUNT:UPDATE
    """
    check_user_set(current_user, UserSet.AGENCY_AND_BUSINESS)
    business = await BusinessAccountModel.get_or_exception(pk=id)
    if current_user.type in UserSet.AGENCY.value:
        # If the current user is an admin, they can update any field
        data = data.dict(exclude_unset=True)
    else:
        # If the current user is not an admin, they can only update certain fields
        if business.is_deleted:
            raise OWJException("E1032")
        if current_user.business_id != business.pk:
            raise OWJPermissionException()

        data = BusinessAccountUpdateRequest(**data.dict()).dict(exclude_unset=True)

    business.update_from_dict(data)
    await business.save()
    return {"data": business}
