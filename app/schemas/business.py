from typing import Optional

from pydantic import UUID4, BaseModel, Field
from tortoise.contrib.pydantic import pydantic_model_creator
from app.models.business import BusinessAccount as BusinessAccountModel
from owjcommon.schemas import Response, PhoneNumber, PaginatedResult, Filters
from pydantic import validator


BusinessAccount = pydantic_model_creator(BusinessAccountModel, name="BusinessAccount")


class BusinessAccountCreateRequest(PhoneNumber):
    name: str = Field(..., description="Name of the business account")


class BusinessAccountUpdateRequest(BaseModel):
    name: Optional[str] = Field(None, description="Name of the business account")


class AgencyBusinessAccountUpdateRequest(BusinessAccountUpdateRequest):
    is_deleted: Optional[bool] = Field(
        None, description="Whether the business account is deleted or not"
    )


class BusinessAccountFilters(Filters):
    name: Optional[str] = Field(None, description="Name of the business account")


class BusinessAccountResponse(Response):
    data: BusinessAccount = Field(..., description="Business account data")


class BusinessAccountsResponse(PaginatedResult):
    items: list[BusinessAccount] = Field(..., description="List of business accounts")
