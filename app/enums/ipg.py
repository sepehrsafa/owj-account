from enum import Enum


class IPGType(str, Enum):
    SEP = "SEP"
    NEXTPAY = "NEXTPAY"


class TransactionStatus(str, Enum):
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    PENDING = "PENDING"
    CANCELED = "CANCELED"
    DISCREPANCY = "DISCREPANCY"
    UNKNOWN = "UNKNOWN",
    VERIFYING = "VERIFYING"