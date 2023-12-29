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
    name: str = Field(..., example="IPG Name", description="Name of the IPG")
    type: IPGType = Field(..., example=IPGType.SEP, description="IPG provider type")
    terminal_id: Optional[str] = Field(
        None, example="12212", description="Terminal ID of the IPG"
    )
    merchant_id: Optional[str] = Field(
        None, example="12212", description="Merchant ID of the IPG"
    )
    merchant_key: Optional[str] = Field(
        None, example="12212", description="Merchant Key of the IPG"
    )
    password: Optional[str] = Field(
        None, example="12212", description="Password of the IPG"
    )
    callback_url: str = Field(
        ...,
        example="https://owj.app/sep/callback",
        description="Callback URL, This should be the backend url that handles the callback from the IPG",
    )
    currency: CurrencyChoices = Field(
        ..., example=CurrencyChoices.IRR, description="Currency of the IPG"
    )
    priority: int = Field(
        ...,
        example=0,
        description="Priority of the IPG, IPGs with higher priority will be used first",
    )
    is_active: bool = Field(
        ..., example=True, description="Whether the IPG is active or not"
    )
    url: str = Field(..., example="https://sep.com", description="URL of the IPG API")


class IPGUpdateRequest(BaseModel):
    name: Optional[str] = Field(None, description="Name of the IPG")
    type: Optional[IPGType] = Field(None, description="IPG provider type")
    terminal_id: Optional[str] = Field(None, description="Terminal ID of the IPG")
    merchant_id: Optional[str] = Field(None, description="Merchant ID of the IPG")
    merchant_key: Optional[str] = Field(None, description="Merchant Key of the IPG")
    password: Optional[str] = Field(None, description="Password of the IPG")
    callback_url: Optional[str] = Field(
        None,
        description="Callback URL, This should be the backend url that handles the callback from the IPG",
    )
    currency: Optional[CurrencyChoices] = Field(None, description="Currency of the IPG")
    priority: Optional[int] = Field(
        None,
        description="Priority of the IPG, IPGs with higher priority will be used first",
    )
    is_active: Optional[bool] = Field(
        None, description="Whether the IPG is active or not"
    )
    url: Optional[str] = Field(None, description="URL of the IPG API")


class IPGFilter(Filters):
    name: Optional[str] = Field(None, description="Name of the IPG")
    type: Optional[IPGType] = Field(None, description="IPG provider type")
    terminal_id: Optional[str] = Field(None, description="Terminal ID of the IPG")
    merchant_id: Optional[str] = Field(None, description="Merchant ID of the IPG")
    merchant_key: Optional[str] = Field(None, description="Merchant Key of the IPG")
    currency: Optional[CurrencyChoices] = Field(None, description="Currency of the IPG")
    priority: Optional[int] = Field(
        None,
        description="Priority of the IPG, IPGs with higher priority will be used first",
    )
    is_active: Optional[bool] = Field(
        None, description="Whether the IPG is active or not"
    )


IPG = pydantic_model_creator(IPGModel, name="IPG")


class IPGsResponse(PaginatedResult):
    items: list[IPG] = Field(..., description="List of IPGs")


class IPGResponse(Response):
    data: IPG = Field(..., description="IPG data")


Wallet = pydantic_model_creator(WalletModel, name="Wallet")


class WalletsResponse(Response):
    items: list[Wallet] = Field(..., description="List of wallets")


class WalletResponse(Response):
    data: Wallet = Field(..., description="Wallet data")


class WalletTopOffRequest(BaseModel):
    amount: Decimal = Field(..., ge=Decimal(0), description="Amount to top off")
    currency: CurrencyChoices = Field(
        default=CurrencyChoices.IRR,
        example=CurrencyChoices.IRR,
        description="Currency of the top off",
    )
    note: Optional[str] = Field(None, description="Note for the top off")
    reference: Optional[str] = Field(None, description="Reference for the top off")
    return_url: str = Field(
        ...,
        description="URL to redirect after top off. This should be the frontend url that handles the redirect from backend",
    )


class WalletUpdate(BaseModel):
    limit: Decimal = Field(..., ge=Decimal(0), description="Limit of the wallet")
    currency: CurrencyChoices = Field(
        default=CurrencyChoices.IRR,
        example=CurrencyChoices.IRR,
        description="Currency of the wallet",
    )


class WalletTopOffResponse(Response):
    type: str = Field(
        "redirect", description="Determines how to handel top off on frontend"
    )
    url: str = Field(..., description="URL to redirect to IPG")
    token: str = Field(
        ...,
        description="Token to send to IPG. if type is redirect, this is already added to the url",
    )


class _WalletTransactionRequest(BaseModel):
    amount: Decimal = Field(..., ge=Decimal(0), description="Amount of the transaction")
    currency: CurrencyChoices = Field(
        default=CurrencyChoices.IRR,
        example=CurrencyChoices.IRR,
        description="Currency of the transaction",
    )
    note: Optional[str] = Field(None, description="Note for the transaction")
    reference: Optional[str] = Field(
        None, description="Reference for the transaction. Example Flight Sale ID"
    )


class WalletTransactionRequestByUserID(_WalletTransactionRequest):
    user_id: int = Field(..., description="ID of the user")


class WalletTransactionRequestByBusinessID(_WalletTransactionRequest):
    business_id: int = Field(..., description="ID of the business")


WalletTransaction = pydantic_model_creator(
    WalletTransactionModel, name="WalletTransaction"
)


class WalletTransactionsResponse(PaginatedResult):
    items: list[WalletTransaction] = Field(
        ..., description="List of wallet transactions"
    )


class WalletTransactionResponse(Response):
    data: WalletTransaction = Field(..., description="Wallet transaction data")


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
    items: list[IPGTransaction] = Field(..., description="List of IPG transactions")


class IPGTransactionResponse(Response):
    data: IPGTransaction = Field(..., description="IPG transaction data")


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
