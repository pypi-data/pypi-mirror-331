"""
Data models for the Leja Recharge SDK.
"""

from typing import List, Optional, TypeVar, Generic
from pydantic import BaseModel, Field

T = TypeVar('T')


class AirtimeRecipient(BaseModel):
    """Model for an airtime recipient."""
    phone_number: str = Field(..., description="Recipient's phone number")
    amount: float = Field(..., description="Amount of airtime to purchase")
    country: str = Field(..., description="Country code for the recipient")


class AirtimePurchaseRequest(BaseModel):
    """Model for airtime purchase request."""
    phone_number: str = Field(..., description="Sender's phone number")
    recipients: List[AirtimeRecipient] = Field(..., description="List of recipients")
    is_async: bool = Field(True, description="Whether to process the request asynchronously")
    callback_url: Optional[str] = Field(None, description="Callback URL for async requests")


class CountryResponse(BaseModel):
    """Model for country information response."""
    code: str = Field(..., description="Country code")
    country_name: str = Field(..., description="Full country name")
    iso2: str = Field(..., description="ISO 2 country code")
    iso3: str = Field(..., description="ISO 3 country code")
    currency: str = Field(..., description="Country currency code")


class TransactionResponse(BaseModel):
    """Model for transaction response."""
    tracking_id: str = Field(..., description="Unique tracking ID")
    external_id: str = Field(..., description="External transaction ID")
    sender_phone: str = Field(..., description="Sender's phone number")
    beneficiary_phone: str = Field(..., description="Recipient's phone number")
    amount: float = Field(..., description="Transaction amount")
    beneficiary_country: str = Field(..., description="Recipient's country")
    beneficiary_currency: str = Field(..., description="Recipient's currency")
    status: str = Field(..., description="Transaction status")
    failure_reason: Optional[str] = Field(None, description="Reason for failure if any")
    created_at: str = Field(..., description="Transaction creation timestamp")


class BalanceResponse(BaseModel):
    """Model for account balance response."""
    balance: float = Field(..., description="Current account balance")
    currency: str = Field(..., description="Currency of the balance")


class PaginationMeta(BaseModel):
    """Model for pagination metadata."""
    total: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page number")
    limit: int = Field(..., description="Items per page")


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic model for paginated responses."""
    data: List[T] = Field(..., description="List of items")
    meta: PaginationMeta = Field(..., description="Pagination metadata")

    @classmethod
    def from_dict(cls, data: dict, item_class: type) -> 'PaginatedResponse[T]':
        """Create a paginated response from a dictionary."""
        return cls(
            data=[item_class(**item) for item in data["data"]],
            meta=PaginationMeta(**data["meta"])
        ) 