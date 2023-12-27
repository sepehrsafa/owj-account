from tortoise import fields, models
from owjcommon.enums import CurrencyChoices
from owjcommon.models import AuditableModel
from .audit import AuditLog
from app.enums import IPGType, TransactionStatus


class Wallet(AuditableModel):
    user = fields.ForeignKeyField("models.UserAccount", related_name="wallets")
    business = fields.ForeignKeyField(
        "models.BusinessAccount", related_name="wallets", null=True
    )
    limit = fields.DecimalField(max_digits=20, decimal_places=2, default=0)
    amount = fields.DecimalField(max_digits=20, decimal_places=2, default=0)
    currency = fields.CharEnumField(CurrencyChoices)
    audit_log_class = AuditLog

    class Meta:
        table = "wallets"
        unique_together = ("user", "currency")


class WalletTransaction(AuditableModel):
    wallet = fields.ForeignKeyField("models.Wallet", related_name="transactions")
    amount = fields.DecimalField(max_digits=20, decimal_places=2, default=0)
    currency = fields.CharEnumField(CurrencyChoices, default=CurrencyChoices.IRR)
    preformed_by = fields.ForeignKeyField(
        "models.UserAccount", related_name="wallet_transactions"
    )
    note = fields.TextField(null=True)
    reference = fields.CharField(max_length=100, null=True)
    balance = fields.DecimalField(max_digits=20, decimal_places=2, default=0)
    audit_log_class = AuditLog

    class Meta:
        table = "wallet_transactions"
        ordering = ["-created_at"]


class IPG(AuditableModel):
    name = fields.CharField(max_length=100)
    type = fields.CharEnumField(IPGType)
    terminal_id = fields.CharField(max_length=100, null=True)
    merchant_id = fields.CharField(max_length=100, null=True)
    merchant_key = fields.CharField(max_length=100, null=True)
    password = fields.CharField(max_length=100, null=True)
    callback_url = fields.CharField(max_length=100)
    currency = fields.CharEnumField(CurrencyChoices, default=CurrencyChoices.IRR)
    priority = fields.IntField(default=0)
    is_active = fields.BooleanField(default=True)
    url = fields.CharField(max_length=100)
    audit_log_class = AuditLog

    class Meta:
        table = "ipgs"


class IPGTransaction(AuditableModel):
    user = fields.ForeignKeyField("models.UserAccount", related_name="ipg_transactions")
    ipg = fields.ForeignKeyField("models.IPG", related_name="transactions")
    status = fields.CharEnumField(TransactionStatus, default=TransactionStatus.PENDING)
    type = fields.CharField(max_length=100)
    wallet = fields.ForeignKeyField("models.Wallet", related_name="ipg_transactions", null=True)
    amount = fields.DecimalField(max_digits=20, decimal_places=2, default=0)
    currency = fields.CharEnumField(CurrencyChoices, default=CurrencyChoices.IRR)
    card_number = fields.CharField(max_length=100, null=True)
    card_type = fields.CharField(max_length=100, null=True)
    reference_id = fields.CharField(max_length=100, null=True)
    note = fields.TextField(null=True)
    ipg_reference_id = fields.CharField(max_length=100, null=True)
    shaparak_reference_id = fields.CharField(max_length=100, null=True)
    trace_number = fields.CharField(max_length=100, null=True)
    token = fields.CharField(max_length=100, null=True)
    audit_log_class = AuditLog

    class Meta:
        table = "ipg_transactions"
        ordering = ["-created_at"]

