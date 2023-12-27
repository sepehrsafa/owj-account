from pydantic import UUID4, BaseModel, Field

from tortoise.contrib.pydantic import pydantic_model_creator
from owjcommon.enums import CurrencyChoices
from owjcommon.schemas import Response, PaginatedResult, Filters
from decimal import Decimal
from typing import Optional
from app.enums import IPGType, TransactionStatus

from app.models.finance import (
    IPG as IPGModel,
    IPGTransaction as IPGTransactionModel,
    Wallet as WalletModel,
    WalletTransaction as WalletTransactionModel,
)


class IPGRequest(BaseModel):
    name: str
    type: IPGType = Field(..., example=IPGType.SEP)
    terminal_id: Optional[str] = None
    merchant_id: Optional[str] = None
    merchant_key: Optional[str] = None
    password: Optional[str] = None
    callback_url: str
    currency: CurrencyChoices = Field(..., example=CurrencyChoices.IRR)
    priority: int = Field(..., example=0)
    is_active: bool = Field(..., example=True)
    url: str


class IPGUpdateRequest(BaseModel):
    name: Optional[str] = None
    type: Optional[IPGType] = None
    terminal_id: Optional[str] = None
    merchant_id: Optional[str] = None
    merchant_key: Optional[str] = None
    password: Optional[str] = None
    callback_url: Optional[str] = None
    currency: Optional[CurrencyChoices] = None
    priority: Optional[int] = None
    is_active: Optional[bool] = None
    url: Optional[str] = None


class IPGFilter(Filters):
    name: Optional[str] = None
    type: Optional[IPGType] = None
    terminal_id: Optional[str] = None
    merchant_id: Optional[str] = None
    merchant_key: Optional[str] = None
    currency: Optional[CurrencyChoices] = None
    priority: Optional[int] = None
    is_active: Optional[bool] = None


IPG = pydantic_model_creator(IPGModel, name="IPG")


class IPGsResponse(PaginatedResult):
    items: list[IPG]


class IPGResponse(Response):
    data: IPG


Wallet = pydantic_model_creator(WalletModel, name="Wallet")


class WalletsResponse(Response):
    items: list[Wallet]


class WalletResponse(Response):
    data: Wallet


class WalletTopOffRequest(BaseModel):
    amount: Decimal = Field(..., ge=Decimal(0))
    currency: CurrencyChoices = Field(
        default=CurrencyChoices.IRR, example=CurrencyChoices.IRR
    )
    note: Optional[str] = None
    reference: Optional[str]
    return_url: str


class WalletUpdate(BaseModel):
    limit: Decimal = Field(..., ge=Decimal(0))
    currency: CurrencyChoices = Field(
        default=CurrencyChoices.IRR, example=CurrencyChoices.IRR
    )


class WalletTopOffResponse(Response):
    type: str = "redirect"
    url: str
    token: str


class _WalletTransactionRequest(BaseModel):
    amount: Decimal = Field(..., ge=Decimal(0))
    currency: CurrencyChoices = Field(
        default=CurrencyChoices.IRR, example=CurrencyChoices.IRR
    )
    note: Optional[str] = None
    reference: Optional[str] = None


class WalletTransactionRequestByUserID(_WalletTransactionRequest):
    user_id: int


class WalletTransactionRequestByBusinessID(_WalletTransactionRequest):
    business_id: int


WalletTransaction = pydantic_model_creator(
    WalletTransactionModel, name="WalletTransaction"
)


class WalletTransactionsResponse(PaginatedResult):
    items: list[WalletTransaction]


class WalletTransactionResponse(Response):
    data: WalletTransaction


class WalletTransactionFilter(Filters):
    amount: Optional[Decimal] = None
    currency: Optional[CurrencyChoices] = None
    note: Optional[str] = None
    reference: Optional[str] = None
    preformed_by: Optional[int] = None
    balance: Optional[Decimal] = None
    wallet: Optional[int] = None


IPGTransaction = pydantic_model_creator(IPGTransactionModel, name="IPGTransaction")


class IPGTransactionsResponse(PaginatedResult):
    items: list[IPGTransaction]


class IPGTransactionResponse(Response):
    data: IPGTransaction


class IPGTransactionFilter(Filters):
    user: Optional[int] = None
    ipg: Optional[int] = None
    status: Optional[TransactionStatus] = None
    type: Optional[str] = None
    wallet: Optional[int] = None
    amount: Optional[Decimal] = None
    currency: Optional[CurrencyChoices] = None
    card_number: Optional[str] = None
    card_type: Optional[str] = None
    reference_id: Optional[str] = None
    note: Optional[str] = None
    shaparak_reference_id: Optional[str] = None
    trace_number: Optional[str] = None
    token: Optional[str] = None
