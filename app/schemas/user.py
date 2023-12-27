from typing import Optional

from pydantic import UUID4, BaseModel, EmailStr, validator, Field

from owjcommon.enums import UserTypeChoices


from owjcommon.schemas import Response, PaginatedResult, Password, Filters, PhoneNumber, OwjBaseModel
from owjcommon.validators import is_valid_phone_number
import datetime
from .business import BusinessAccount
from .finance import Wallet


class SimpleUserAccountCreateRequest(PhoneNumber):
    pass


class UserAccountCreateRequest(PhoneNumber):
    first_name: str = Field(..., example="John")
    last_name: str = Field(..., example="Doe")
    type: Optional[UserTypeChoices] = Field(
        default=UserTypeChoices.REGULAR_USER,
        example=UserTypeChoices.REGULAR_USER,
        description="This will be set automatically based on the user type of the user who is creating this user account.",
    )
    email: Optional[EmailStr] = Field(
        None,
        example="John@owj.app",
        description="If not provided, the user will be created without an email.",
    )
    business_id: Optional[int] = Field(
        None,
        example=1,
        description="If not provided, the user will be created without a business. It is required to create a business.",
    )


class UserAccount(PhoneNumber, OwjBaseModel):
    uuid: UUID4
    type: UserTypeChoices
    email: Optional[EmailStr] = Field(None, example="sepehr@owj.app")
    first_name: Optional[str] = Field(None, example="Sepehr")
    last_name: Optional[str] = Field(None, example="Safa")


class UserAccountFull(UserAccount):
    iran_national_id: Optional[str] = Field(
        None, example="1234567890", description="Iranian National ID"
    )
    is_active: bool
    is_buying_allowed: bool
    is_phone_number_verified: bool
    is_email_verified: bool
    is_only_otp_login_allowed: bool
    is_2fa_on: bool
    business_id: Optional[int] = Field(
        None, example=1, description="Business ID if the user is a business user"
    )
    iban_number: Optional[str] = Field(
        None,
        example="IR123456789012345678901234",
        description="Iran IBAN (Shaba) Number",
    )
    created_at: datetime.datetime
    updated_at: datetime.datetime


class UserAccountUpdateRequest(BaseModel):
    first_name: Optional[str] = Field(None, example="Sepehr")
    last_name: Optional[str] = Field(None, example="Safa")
    email: Optional[EmailStr] = Field(None, example="sepehr@owj.app")
    iran_national_id: Optional[str] = Field(
        None, example="1234567890", description="Iranian National ID"
    )
    iban_number: Optional[str] = Field(
        None,
        example="IR123456789012345678901234",
        description="Iran IBAN (Shaba) Number",
    )


class UserAccountUpdateRequestByAgency(UserAccountUpdateRequest, PhoneNumber):
    type: Optional[UserTypeChoices] = None
    is_active: Optional[bool] = None
    is_buying_allowed: Optional[bool] = None
    is_phone_number_verified: Optional[bool] = None
    is_email_verified: Optional[bool] = None
    is_only_otp_login_allowed: Optional[bool] = None
    is_2fa_on: Optional[bool] = None
    business_id: Optional[int] = Field(
        None, example=1, description="Business ID if the user is a business user"
    )


class UserAccountMe(UserAccountFull):
    wallets: list[Wallet]
    business: Optional[BusinessAccount] = None
    permissions: list[str]


class UserAccountMeResponse(Response):
    data: UserAccountMe


class UserAccountResponse(Response):
    data: UserAccountFull


class UserAccountsResponse(PaginatedResult):
    items: list[UserAccountFull]


class UserAccountFilters(Filters):
    phone_number: Optional[str] = None
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    type: Optional[UserTypeChoices] = None
    is_active: Optional[bool] = None
    is_buying_allowed: Optional[bool] = None
    is_phone_number_verified: Optional[bool] = None
    is_email_verified: Optional[bool] = None
    is_only_otp_login_allowed: Optional[bool] = None
    is_2fa_on: Optional[bool] = None
    business_id: Optional[int] = None
    iran_national_id: Optional[str] = None
    iban_number: Optional[str] = None
