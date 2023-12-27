import uuid
from datetime import datetime, timedelta

import pytz
from app.config import settings
from app.schemas.auth import TokenResponse
from app.services.auth import (
    check_otp,
    check_password,
    create_access_token,
    get_otp,
    get_otp_hash,
    hash_password,
)
from tortoise import fields, models

from owjcommon.enums import USER_TYPE_PERMISSIONS, UserTypeChoices
from owjcommon.exceptions import OWJException
from owjcommon.models import AuditableModel
from owjcommon.validators import is_valid_email, is_valid_phone_number

from .audit import AuditLog
from .token import UserToken


class UserAccount(AuditableModel):
    uuid = fields.UUIDField(unique=True, default=uuid.uuid4, index=True)
    type = fields.CharEnumField(UserTypeChoices, default=UserTypeChoices.REGULAR_USER)

    phone_number = fields.CharField(max_length=30, unique=True, null=False)
    email = fields.CharField(max_length=150, unique=True, null=True)

    first_name = fields.CharField(max_length=100, null=True)
    last_name = fields.CharField(max_length=110, null=True)
    iran_national_id = fields.CharField(max_length=10, null=True)
    iban_number = fields.CharField(max_length=26, null=True)

    is_active = fields.BooleanField(default=True)
    is_buying_allowed = fields.BooleanField(default=True)
    is_phone_number_verified = fields.BooleanField(default=False)
    is_email_verified = fields.BooleanField(default=False)
    is_only_otp_login_allowed = fields.BooleanField(default=True)
    is_2fa_on = fields.BooleanField(default=False)

    otp_hash = fields.CharField(max_length=300, default=get_otp_hash)
    last_otp_sent = fields.DatetimeField(null=True)

    hashed_password = fields.CharField(max_length=1000, null=True)

    business = fields.ForeignKeyField(
        "models.BusinessAccount", related_name="users", null=True
    )

    audit_log_class = AuditLog

    class Meta:
        table = "user_account"

    def __str__(self):
        return f"{self.phone_number}"

    async def check_otp(self, code: str) -> bool:
        return await check_otp(self.otp_hash, code)

    async def get_otp(self) -> str:
        if self.last_otp_sent:
            time_diff = datetime.now(tz=pytz.utc) - self.last_otp_sent
            if time_diff.seconds < settings.otp.resend_timeout:
                raise OWJException("E1014")
        otp = await get_otp(self.otp_hash)
        self.last_otp_sent = datetime.now(tz=pytz.utc)
        await self.save()
        return str(otp)

    async def set_password(self, password: str, save=True) -> None:
        self.hashed_password = await hash_password(password)
        if save:
            await self.save()

    async def check_password(self, password) -> bool:
        return await check_password(self.hashed_password, password)

    async def get_permissions(self) -> list[str]:
        assigned_permissions = await self.user_groups.all().values_list(
            "permissions", flat=True
        )
        permissions = USER_TYPE_PERMISSIONS.get(self.type, [])

        for permission in assigned_permissions:
            for sub_permission in permission:
                permissions.append(sub_permission)

        return list(set(permissions))

    async def create_access_token(self) -> TokenResponse:
        jti = uuid.uuid4()
        refresh_expire = datetime.utcnow() + timedelta(
            days=settings.jwt.refresh_token_expire_days
        )

        permissions = await self.get_permissions()

        token: TokenResponse = await create_access_token(
            self.id,
            self.uuid,
            jti,
            self.business_id,
            self.phone_number,
            self.email,
            self.type,
            permissions,
        )
        await UserToken.create(
            jti=jti,
            user=self,
            expire=refresh_expire,
        )
        return token

    @classmethod
    async def get_by_identifier(cls, identifier: str) -> "UserAccount":
        if is_valid_phone_number(identifier):
            user_field = "phone_number"
        elif is_valid_email(identifier):
            user_field = "email"
        else:
            raise OWJException("E1002")
        query = {user_field: identifier.lower()}

        user = await cls.get_or_none(**query)

        if not user:
            raise OWJException("E1002")

        if not user.is_active:
            raise OWJException("E1013")

        return user
