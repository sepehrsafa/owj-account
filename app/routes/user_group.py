from typing import Annotated
from app.models.user import UserAccount
from app.models.user_group import UserGroup
from owjcommon.schemas import Response
from app.schemas.user_group import (
    AddUserToGroupRequest,
    CreateGroupRequest,
    GroupsResponse,
    GroupResponse,
    UpdateGroupRequest,
    UserGroupFilters,
    MyGroupsResponse,
)
from app.services.auth.utils import get_current_active_user, check_user_set
from fastapi import APIRouter, Depends, Request, Security
from pydantic import UUID4

from owjcommon.dependencies import get_trace_id, pagination
from owjcommon.enums import UserPermission, UserSet
from owjcommon.exceptions import OWJException, OWJPermissionException
from owjcommon.models import get_paginated_results_with_filter
from owjcommon.response import responses

router = APIRouter(tags=["User Group"])


@router.post("", response_model=GroupResponse, responses=responses)
async def create_group(
    data: CreateGroupRequest,
    current_user: Annotated = Security(
        get_current_active_user, scopes=[UserPermission.USER_GROUP_CREATE]
    ),
):
    """
    Type and Scope:

    - **Type**: AGENCY  User Set
    - **Scope**: USER_GROUP:READ
    """
    check_user_set(current_user, UserSet.AGENCY)
    group: UserGroup = await UserGroup.create(
        name=data.name,
        permissions=data.permissions,
    )

    await group.fetch_related("users")

    return {"data": group}


@router.get("", response_model=GroupsResponse, responses=responses)
async def get_groups(
    current_user: Annotated = Security(
        get_current_active_user, scopes=[UserPermission.USER_GROUP_READ]
    ),
    pagination=Depends(pagination),
    filters: UserGroupFilters = Depends(),
    trace_id=Depends(get_trace_id),
):
    """
    Type and Scope:

    - **Type**: AGENCY  User Set
    - **Scope**: USER_GROUP:READ
    """
    check_user_set(current_user, UserSet.AGENCY)
    filters = filters.dict(exclude_unset=True)
    return await get_paginated_results_with_filter(
        UserGroup,
        pagination["offset"],
        pagination["size"],
        user_filters=filters,
        prefetch_related=["users"],
    )


@router.get("/me", response_model=MyGroupsResponse, responses=responses)
async def get_my_groups(
    current_user: Annotated = Security(get_current_active_user),
):
    """
    Type and Scope:

    - **Type**: Any User Set
    - **Scope**: None
    """
    groups = await current_user.user_groups.all()
    return {"items": groups}


@router.get("/user/{user_id}", response_model=MyGroupsResponse, responses=responses)
async def get_user_groups(
    user_id: int,
    current_user: Annotated = Security(
        get_current_active_user, scopes=[UserPermission.USER_GROUP_READ]
    ),
):
    """
    Type and Scope:

    - **Type**: AGENCY AND BUSINESS User Set
    - **Scope**: None
    """
    check_user_set(current_user, UserSet.AGENCY_AND_BUSINESS)
    if current_user.type in UserSet.BUSINESS.value:
        user = await UserAccount.get_or_exception(
            id=user_id, business_id=current_user.business_id
        )
    else:
        user = await UserAccount.get_or_exception(id=user_id)
    groups = await user.user_groups.all()
    return {"items": groups}


@router.get("/{id}", response_model=GroupResponse, responses=responses)
async def get_group(
    id: int,
    current_user: Annotated = Security(
        get_current_active_user, scopes=[UserPermission.USER_GROUP_READ]
    ),
):
    """
    Type and Scope:

    - **Type**: AGENCY  User Set
    - **Scope**: USER_GROUP:READ
    """
    check_user_set(current_user, UserSet.AGENCY)
    group: UserGroup = await UserGroup.get_or_exception(
        id=id, prefetch_related=["users"]
    )
    return {"data": group}


@router.put("/{id}", response_model=GroupResponse, responses=responses)
async def update_group(
    id: int,
    data: UpdateGroupRequest,
    current_user: Annotated = Security(
        get_current_active_user, scopes=[UserPermission.USER_GROUP_UPDATE]
    ),
):
    """
    Type and Scope:

    - **Type**: AGENCY  User Set
    - **Scope**: USER_GROUP:UPDATE
    """
    group: UserGroup = await UserGroup.get_or_exception(
        id=id, prefetch_related=["users"]
    )
    group = await group.update_from_dict(data.dict(exclude_unset=True))
    return {"data": group}


@router.delete("/{id}", response_model=Response, responses=responses)
async def delete_group(
    id: int,
    current_user: Annotated = Security(
        get_current_active_user, scopes=[UserPermission.USER_GROUP_DELETE]
    ),
):
    """
    Type and Scope:

    - **Type**: AGENCY  User Set
    - **Scope**: USER_GROUP:DELETE
    """
    group: UserGroup = await UserGroup.get_or_exception(id=id)
    await group.delete()
    return Response()


@router.post("/{id}/add", response_model=GroupResponse, responses=responses)
async def add_user_to_group(
    id: int,
    data: AddUserToGroupRequest,
    current_user: Annotated = Security(
        get_current_active_user, scopes=[UserPermission.USER_GROUP_ADD_USER]
    ),
):
    """
    Type and Scope:

    - **Type**: AGENCY  User Set
    - **Scope**: USER_GROUP:ADD_USER
    """
    group: UserGroup = await UserGroup.get_or_exception(
        id=id, prefetch_related=["users"]
    )

    await group.add_users(data.user_ids)

    await group.fetch_related("users")

    return {"data": group}


@router.delete("/{id}/remove", response_model=GroupResponse, responses=responses)
async def remove_user_from_group(
    id: int,
    data: AddUserToGroupRequest,
    current_user: Annotated = Security(
        get_current_active_user, scopes=[UserPermission.USER_GROUP_READ]
    ),
):
    """
    Type and Scope:

    - **Type**: AGENCY  User Set
    - **Scope**: USER_GROUP:ADD_USER
    """
    group: UserGroup = await UserGroup.get_or_exception(
        id=id, prefetch_related=["users"]
    )

    await group.remove_users(data.user_ids)

    await group.fetch_related("users")

    return {"data": group}
