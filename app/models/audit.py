from owjcommon.models import AuditLogBase


class AuditLog(AuditLogBase):
    class Meta:
        table = "account_audit_log"
        table_description = "Audit Log"
        ordering = ["-timestamp"]
        verbose_name = "Audit Log"
        verbose_name_plural = "Audit Logs"
