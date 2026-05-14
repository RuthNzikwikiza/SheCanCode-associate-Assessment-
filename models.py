from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class PaymentRequest(BaseModel):
    amount: float = Field(..., gt=0, description="Amount to charge (must be > 0)")
    currency: str = Field(..., min_length=1, description="Currency code e.g. GHS, USD")

    def to_fingerprint(self) -> str:
        return f"{self.amount}:{self.currency.upper().strip()}"


class PaymentResponse(BaseModel):
    status: str
    message: str
    transaction_id: str
    idempotency_key: str
    processed_at: str


class ProcessingStatus(str, Enum):
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"


class IdempotencyRecord:
    def __init__(
        self,
        request_fingerprint: str,
        status: ProcessingStatus,
        created_at: datetime,
        response: Optional[PaymentResponse] = None,
        http_status_code: int = 201,
    ):
        self.request_fingerprint = request_fingerprint
        self.status = status
        self.created_at = created_at
        self.response = response
        self.http_status_code = http_status_code


class ErrorResponse(BaseModel):
    error: str
    message: str
    timestamp: str