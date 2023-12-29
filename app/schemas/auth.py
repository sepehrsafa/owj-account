from typing import Optional

from pydantic import UUID4, BaseModel, validator, Field

from app.config import settings
from owjcommon.enums import UserPermission, UserTypeChoices
from owjcommon.validators import is_valid_email, is_valid_phone_number

from owjcommon.schemas import Password, Response


class TokenResponse(Response):
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(..., description="Type of token")


class TokenData(BaseModel):
    id: int
    sub: str
    business: Optional[str] = None
    phone_number: str
    email: Optional[str] = None
    exp: int
    scopes: list[UserPermission]
    type: UserTypeChoices
    token_type: str


class RefreshTokenData(BaseModel):
    sub: str
    exp: int
    token_type: str
    jti: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str = Field(..., description="JWT refresh token")


class OTPResponse(Response):
    resend_timeout: int = Field(
        settings.otp.resend_timeout,
        description="Time in seconds after which OTP can be resent",
    )


class UsernamePasswordLoginRequest(Password):
    username: str = Field(
        ..., description="Username of the user (email or phone number)"
    )
    otp: Optional[str] = Field(
        None, description="OTP for 2FA. Required if 2FA is enabled"
    )

    @validator("username", pre=True, always=True)
    def validate_username(cls, v):
        if not (is_valid_email(v) or is_valid_phone_number(v)):
            raise ValueError(
                "Username is Invalid. Provide valid email or use +E64 format for phone numbers."
            )
        return v.lower()

    @validator("otp", pre=True, always=True)
    def validate_otp(cls, v):
        if v and len(v) != settings.otp.digits:
            raise ValueError("Invalid OTP length")
        return v.lower()


class OTPRequest(BaseModel):
    phone_number: str = Field(
        ...,
        description="Phone number of the user in +E64 format",
        example="+919876543210",
    )

    @validator("phone_number", pre=True, always=True)
    def validate_phone_number(cls, v):
        if not is_valid_phone_number(v):
            raise ValueError("Invalid phone number. Use +E64 format.")
        return v.lower()


class OTPLoginRequest(OTPRequest):
    otp: str = Field(..., description="One time password (OTP)")

    @validator("otp", pre=True, always=True)
    def validate_otp(cls, v):
        if len(v) != settings.otp.digits:
            raise ValueError("Invalid OTP length")
        return v.lower()


class SetPasswordRequest(Password):
    confirm_password: str = Field(..., description="Confirm password")

    @validator("confirm_password", pre=True, always=True)
    def validate_confirm_password(cls, v, values):
        if "password" in values and v != values["password"]:
            raise ValueError("Passwords do not match")
        return v
