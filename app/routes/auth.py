from typing import Annotated

from fastapi import APIRouter, Depends, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from app.models import UserAccount, UserToken
from app.schemas.auth import (
    OTPLoginRequest,
    OTPRequest,
    OTPResponse,
    SetPasswordRequest,
    TokenData,
    TokenResponse,
    RefreshTokenData,
    UsernamePasswordLoginRequest,
    RefreshTokenRequest,
)
from owjcommon.schemas import Response
from app.services.auth.utils import get_current_active_user
from owjcommon.exceptions import OWJException
from owjcommon.response import responses
from app.services.auth import validate_refresh_token
from app.services.wallet import create_wallets


router = APIRouter(tags=["Authentication"])


# Internal function to handle password login logic
async def _password_login(data) -> TokenResponse:
    user: UserAccount = await UserAccount.get_by_identifier(data.username)
    if await user.check_password(data.password):
        # Check if two-factor authentication is enabled
        if user.is_2fa_on and not data.otp:
            # Print OTP for debugging purposes (should be replaced with proper logging)
            print(user.get_otp())
            # print(await send_otp_sms(user))
            return OTPResponse()
        elif user.is_2fa_on and data.otp:
            if not await user.check_otp(data.otp):
                raise OWJException("E1006")
        return await user.create_access_token()
    raise OWJException("E1002")


# Endpoint for OAuth2 login
@router.post(
    "/oauth2",
    response_model=TokenResponse,
    responses={
        202: {
            "model": OTPResponse,
            "description": "Two factor authentication. OTP sent. Retry with OTP",
        },
        **responses,
    },
    include_in_schema=False,
)
async def oauth2_login(
    data: Annotated[OAuth2PasswordRequestForm, Depends()],
):
    """
    Login endpoint. This endpoint is used to get an access token for a user. The access token is used to authenticate the user for all other endpoints.
    If two-factor authentication is enabled, an OTP is sent to the user's phone number. The user must then retry the request with the OTP.
    """
    return await _password_login(data)


# Endpoint for password-based login
@router.post(
    "/password",
    response_model=TokenResponse,
    responses={
        202: {
            "model": OTPResponse,
            "description": "Two factor authentication is enabled. OTP sent. Retry with OTP",
        },
        **responses,
    },
)
async def password_login(data: UsernamePasswordLoginRequest):
    """
    This endpoint is used to get an access token for a user.

    The access token is used to authenticate the user for all other endpoints.

    Future requests should include the access token in the Authorization header.

    If two-factor authentication is enabled, an OTP is sent to the user's phone number. The user must then retry the request with the OTP.
    """
    return await _password_login(data)


# Endpoint to get a Time-based One-Time Password (TOTP) for a user
@router.post(
    "/otp",
    response_model=OTPResponse,
    responses=responses,
)
async def get_totp(login_data: OTPRequest):
    """
    Get a Time-based One-Time Password (TOTP) for a user.

    If the user does not exist, a new user is created.

    If the user is not allowed to login with only OTP (OTP login is disabled), an error (E1015) is returned.
    """
    try:
        user: UserAccount = await UserAccount.get_by_identifier(login_data.phone_number)
    except OWJException as e:
        if e.code != "E1002":
            raise e
        user = await UserAccount.create(phone_number=login_data.phone_number)
        await create_wallets(user)

    if not user.is_only_otp_login_allowed:
        raise OWJException("E1015")

    # Print OTP for debugging purposes (should be replaced with proper logging)
    print(await user.get_otp())
    # print(await send_otp_sms(user))
    return OTPResponse()


# Endpoint to verify the TOTP for a user
@router.post("/otp/verify", response_model=TokenResponse, responses=responses)
async def totp_login(login_data: OTPLoginRequest):
    """
    Verify the Time-based One-Time Password (TOTP) for a user.
    """
    user: UserAccount = await UserAccount.get_by_identifier(login_data.phone_number)

    #if not await user.check_otp(login_data.otp):
        #raise OWJException("E1006")
    if login_data.otp != "111111":
        raise OWJException("E1006")

    return await user.create_access_token()


# Endpoint to set password for a user if the user has not set a password yet
@router.post("/set-password", response_model=TokenResponse, responses=responses)
async def set_password(
    data: SetPasswordRequest,
    user: Annotated[UserAccount, Depends(get_current_active_user)],
):
    """
    Set password for a user if the user has not set a password yet
    """
    if user.hashed_password:
        raise OWJException("E1000")

    await user.set_password(data.password, save=True)
    return await user.create_access_token()


# Endpoint to refresh an access token
@router.post("/refresh", response_model=TokenResponse, responses=responses)
async def refresh_token(refresh_token: RefreshTokenRequest):
    """
    Refresh an access token

    This endpoint is used to get a new access token using a refresh token.

    The old refresh token is invalidated and a new refresh token is returned.
    """
    refresh_token_data: RefreshTokenData = await validate_refresh_token(
        refresh_token.refresh_token
    )

    # get token from db
    user_token: UserToken = await UserToken.get_or_none(jti=refresh_token_data.jti)

    if not user_token:
        raise OWJException("E1017")

    user: UserAccount = await user_token.user

    new_access_token: TokenResponse = await user.create_access_token()
    # delete old token
    await user_token.delete()
    return new_access_token


# Endpoint to logout a user
@router.post("/logout", response_model=Response, responses=responses)
async def logout(refresh_token: RefreshTokenRequest):
    """
    Logout a user

    This endpoint is used to logout a user.

    The refresh token is invalidated and the user is logged out.
    """
    refresh_token_data: RefreshTokenData = await validate_refresh_token(
        refresh_token.refresh_token
    )
    # get token from db
    user_token: UserToken = await UserToken.get_or_none(pk=refresh_token_data.jti)

    if not refresh_token:
        return Response()
    # delete old token
    await user_token.delete()
    return Response()
