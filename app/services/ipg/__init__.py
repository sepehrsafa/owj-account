from app.enums import IPGType
from .nextpay import NextPayClient


def get_ipg_client(type: IPGType):
    if type == IPGType.NEXTPAY:
        return NextPayClient