import uuid

from tortoise import fields, models

from owjcommon.models import AuditableModel
from .user import UserAccount
from .audit import AuditLog
from tortoise.exceptions import DoesNotExist


class UserGroup(AuditableModel):
    name = fields.CharField(max_length=100, unique=True)
    permissions = fields.JSONField(default=list)
    users = fields.ManyToManyField("models.UserAccount", related_name="user_groups")
    audit_log_class = AuditLog

    class Meta:
        table = "user_group"

    async def add_users(self, users: list[str]) -> None:
        # list of user uuids
        try:
            user_objects = await UserAccount.filter(id__in=users)
        except DoesNotExist:
            return

        await self.users.add(*user_objects)

    async def remove_users(self, users: list[str]) -> None:
        # list of user uuids
        try:
            user_objects = await UserAccount.filter(id__in=users)
        except DoesNotExist:
            return

        await self.users.remove(*user_objects)
