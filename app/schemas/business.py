from typing import Optional

from pydantic import UUID4, BaseModel
from tortoise.contrib.pydantic import pydantic_model_creator
from app.models.business import BusinessAccount as BusinessAccountModel
from owjcommon.schemas import Response, PhoneNumber, PaginatedResult, Filters
from pydantic import validator


BusinessAccount = pydantic_model_creator(BusinessAccountModel, name="BusinessAccount")


class BusinessAccountCreateRequest(PhoneNumber):
    name: str


class BusinessAccountUpdateRequest(BaseModel):
    name: Optional[str] = None


class AgencyBusinessAccountUpdateRequest(BusinessAccountUpdateRequest):
    is_deleted: Optional[bool] = None


class BusinessAccountFilters(Filters):
    name: Optional[str] = None


class BusinessAccountResponse(Response):
    data: BusinessAccount


class BusinessAccountsResponse(PaginatedResult):
    items: list[BusinessAccount]
