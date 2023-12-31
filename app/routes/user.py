from typing import Annotated, Union

from app.models import Wallet as WalletModel
from app.models.business import BusinessAccount as BusinessAccountModel
from app.models.user import UserAccount
from app.schemas.business import BusinessAccount
from app.schemas.user import (
    UserAccountCreateRequest,
    UserAccountFilters,
    UserAccountFull,
    UserAccountMe,
    UserAccountMeResponse,
    UserAccountResponse,
    UserAccountsResponse,
    UserAccountUpdateRequest,
    UserAccountUpdateRequestByAgency,
)
from app.services.auth.utils import check_user_set, get_current_active_user
from fastapi import APIRouter, Depends, HTTPException, Security
from pydantic import ValidationError

from owjcommon.dependencies import get_trace_id, pagination
from owjcommon.enums import UserPermission, UserSet, UserTypeChoices
from owjcommon.exceptions import OWJException, OWJPermissionException
from owjcommon.models import get_paginated_results_with_filter
from owjcommon.response import responses

router = APIRouter(
    tags=["User Account"],
)


def get_query_filter(current_user):
    # if regular user, only return itself, if business user, only return users of its business, if agency user, only return all users
    if current_user.type == UserTypeChoices.REGULAR_USER:
        return {"uuid": current_user.uuid}
    elif current_user.type == UserTypeChoices.BUSINESS_USER:
        return {"business": current_user.business}
    elif current_user.type == UserTypeChoices.BUSINESS_SUPERUSER:
        return {"business": current_user.business}
    else:
        return {}


# create create, update, delete, get, list
@router.post("", response_model=UserAccountResponse, responses=responses)
async def create_user_account(
    data: UserAccountCreateRequest,
    current_user: UserAccount = Security(
        get_current_active_user, scopes=[UserPermission.USER_ACCOUNT_CREATE]
    ),
):
    """
    Type and Scope:

    - **Type**: AGENCY or BUSINESS User Set
    - **Scope**: USER_ACCOUNT:CREATE

    Description:

    - **AGENCY_SUPERUSER**: Can create any type of user account, including other AGENCY users. Business is needed if the user type is BUSINESS_USER.
    - **AGENCY_USER**: Can create any type of user account, excluding other AGENCY users. Business is needed if the user type is BUSINESS_USER.
    - **BUSINESS_SUPERUSER and USER**: Can create only **BUSINESS_USER**. The business will be set automatically based on the business of the user who is creating this user account.
    """

    check_user_set(current_user, UserSet.AGENCY_AND_BUSINESS)

    if current_user.type in UserSet.BUSINESS.value:
        data.type = UserTypeChoices.BUSINESS_USER
        data.business_id = current_user.business_id

    if current_user.type == UserTypeChoices.AGENCY_USER and (
        data.type in UserSet.AGENCY.value
        or data.type == UserTypeChoices.BUSINESS_SUPERUSER
    ):
        raise OWJPermissionException()

    if (
        current_user.type in UserSet.AGENCY.value
        and data.type in UserSet.BUSINESS.value
    ):
        if not data.business_id:
            raise OWJException("E1031", 400)

    new_user_account = await UserAccount.create(**data.dict(exclude_unset=True))

    return {"data": new_user_account}



# get all
@router.get("", response_model=UserAccountsResponse, responses=responses)
async def get_user_accounts(
    current_user: UserAccount = Security(
        get_current_active_user, scopes=[UserPermission.USER_ACCOUNT_READ]
    ),
    pagination=Depends(pagination),
    filters: UserAccountFilters = Depends(),
):
    """
    Type and Scope:

    - **Type**: AGENCY or BUSINESS User Set
    - **Scope**: USER_ACCOUNT:READ
    """
    check_user_set(current_user, UserSet.AGENCY_AND_BUSINESS)
    filters = filters.dict(exclude_unset=True)

    return await get_paginated_results_with_filter(
        UserAccount,
        pagination["offset"],
        pagination["size"],
        user_filters=filters,
        system_filters=get_query_filter(current_user),
    )


@router.get("/me", response_model=UserAccountMeResponse, responses=responses)
async def get_my_user_account(
    current_user: UserAccount = Security(get_current_active_user),
):
    """
    Type and Scope:

    - **Type**: Any User Set
    - **Scope**: None
    """
    # get user acount wallets
    business = None
    if current_user.type in UserSet.BUSINESS.value:
        wallets = await WalletModel.filter(business_id=current_user.business_id)
        business = await BusinessAccountModel.get(id=current_user.business_id)
    else:
        wallets = await WalletModel.filter(user=current_user)
    permissions = await current_user.get_permissions()
    data = UserAccountMe(
        **current_user.__dict__,
        wallets=wallets,
        business=business,
        permissions=permissions
    )
    return UserAccountMeResponse(data=data)


@router.put("/me", response_model=UserAccountResponse, responses=responses)
async def update_my_user_account(
    id: int,
    data: UserAccountUpdateRequest,
    current_user: UserAccount = Security(get_current_active_user),
):
    """
    Type and Scope:

    - **Type**: Any User Set
    - **Scope**: None
    """
    current_user.update(**data.dict())
    await current_user.save()
    return {"data": current_user}


@router.get("/{id}", response_model=UserAccountResponse, responses=responses)
async def get_user_account(
    id: int,
    current_user: UserAccount = Security(
        get_current_active_user, scopes=[UserPermission.USER_ACCOUNT_READ]
    ),
):
    """
    Type and Scope:

    - **Type**: AGENCY or BUSINESS User Set
    - **Scope**: USER_ACCOUNT:READ
    """
    check_user_set(current_user, UserSet.AGENCY_AND_BUSINESS)

    if current_user.type == UserSet.BUSINESS:
        user_account = await UserAccount.get_or_exception(
            id=id, business_id=current_user.business_id
        )
    else:
        user_account = await UserAccount.get_or_exception(id=id)

    return {"data": user_account}


@router.put("/{id}", response_model=UserAccountResponse, responses=responses)
async def update_user_account(
    id: int,
    data: Union[UserAccountUpdateRequestByAgency, UserAccountUpdateRequest],
    current_user: UserAccount = Security(
        get_current_active_user, scopes=[UserPermission.USER_ACCOUNT_UPDATE]
    ),
):
    """
    Type and Scope:

    - **Type**: Any User Set
    - **Scope**: USER_ACCOUNT:UPDATE

    Description:
    AGENCY users can update any user account, excluding other AGENCY users. BUSINESS users can update only users of their business. REGULAR users can update only themselves.
    """

    if current_user.type not in UserSet.AGENCY:
        data = UserAccountUpdateRequest(**data)

    data = data.dict(exclude_unset=True)

    if current_user.type in UserSet.REGULAR and current_user.id != id:
        raise OWJPermissionException()

    if current_user.type in UserSet.BUSINESS:
        user_account = await UserAccount.get_or_exception(
            id=id, business_id=current_user.business_id
        )
    else:
        user_account = await UserAccount.get_or_exception(id=id)

    if current_user.type == UserTypeChoices.AGENCY_USER and data.type in [
        UserTypeChoices.AGENCY_USER,
        UserTypeChoices.AGENCY_SUPERUSER,
        UserTypeChoices.BUSINESS_SUPERUSER,
    ]:
        raise OWJPermissionException()

    user_account.update(**data.dict())
    await user_account.save()

    return {"data": user_account}
