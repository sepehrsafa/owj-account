import datetime
import re
from typing import List, Optional, Union

from pydantic import (
    UUID4,
    BaseConfig,
    BaseModel,
    Field,
    ValidationError,
    validator,
)

from owjcommon.exceptions import exception_codes
from owjcommon.enums import UserPermission
from owjcommon.schemas import Response, PaginatedResult, Filters, OwjBaseModel

from .user import UserAccount


class CreateGroupRequest(BaseModel):
    name: str = Field(..., description="Name of the group", example="AdminGroup")
    permissions: list[UserPermission] = Field(
        ..., description="List of permissions", example=[UserPermission.USER_GROUP_READ]
    )


class UserGroupFilters(Filters):
    name: Optional[str] = Field(
        None, description="Name of the group", example="AdminGroup"
    )


class UpdateGroupRequest(BaseModel):
    name: Optional[str] = Field(
        None, description="The new name of the group", example="AdminGroup"
    )
    permissions: Optional[list[UserPermission]] = Field(
        None,
        description="The new list of permissions to be assigned to the group",
        example=[UserPermission.USER_GROUP_ADD_USER, UserPermission.USER_GROUP_READ],
    )


class AddUserToGroupRequest(BaseModel):
    user_ids: list[int] = Field(
        ...,
        description="List of user uuids to be added",
        example=[1, 2, 3, 4, 5],
    )


class BaseGroup(OwjBaseModel):
    name: str = Field(..., description="Name of the group", example="AdminGroup")
    permissions: list[UserPermission] = Field(
        ...,
        description="List of permissions assigned to the group",
        example=[UserPermission.USER_GROUP_ADD_USER, UserPermission.USER_GROUP_READ],
    )


class Group(BaseGroup):
    users: list[UserAccount] = Field(
        ..., description="List of users assigned to the group"
    )


class MyGroupsResponse(Response):
    items: list[BaseGroup] = Field(..., description="List of groups")


class GroupResponse(Response):
    data: Group = Field(..., description="Group data")


class GroupsResponse(PaginatedResult):
    items: list[Group] = Field(..., description="List of groups")
