from app.models.user import UserAccount
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from typing import Annotated
from fastapi import Depends
from .token import validate_token
from owjcommon.exceptions import OWJException, OWJPermissionException
from owjcommon.enums import UserTypeChoices, UserSet
from fastapi import HTTPException, status

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/account/v1/auth/oauth2")


async def get_current_user(
    security_scopes: SecurityScopes,
    token: Annotated[str, Depends(oauth2_scheme)],
):
    token_data = await validate_token(security_scopes, token)
    user = await UserAccount.get_or_none(uuid=token_data.sub)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: Annotated[UserAccount, Depends(get_current_user)],
):
    if current_user.is_active is False:
        raise OWJException("E1013")
    return current_user


def check_user_set(user: UserAccount, user_set: UserSet):
    if user.type not in user_set.value:
        raise OWJException("E1030", 403)
