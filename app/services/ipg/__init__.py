from app.enums import IPGType
from .nextpay import NextPayClient
from .sep import SepClient


def get_ipg_client(type: IPGType):
    if type == IPGType.NEXTPAY:
        return NextPayClient
    if type == IPGType.SEP:
        return SepClient