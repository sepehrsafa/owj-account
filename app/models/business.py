from tortoise import fields

from owjcommon.models import AuditableModel

from .audit import AuditLog


class BusinessAccount(AuditableModel):
    name = fields.CharField(max_length=100)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    is_deleted = fields.BooleanField(default=False)
    audit_log_class = AuditLog

    @property
    def hid(self):
        return f'BS{self.id}'

    class Meta:
        table = "business_account"
