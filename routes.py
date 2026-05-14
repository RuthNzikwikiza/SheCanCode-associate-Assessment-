from fastapi import APIRouter, Header, HTTPException, Response
from datetime import datetime

from models import PaymentRequest
from payment_service import (
    PaymentService,
    IdempotencyConflictException,
)

from store import IdempotencyStore

router = APIRouter()

store = IdempotencyStore()
payment_service = PaymentService(store)


@router.post("/process-payment")
def process_payment(
    payment_request: PaymentRequest,
    response: Response,
    idempotency_key: str = Header(..., alias="Idempotency-Key"),
):
    try:

        result, status_code, cache_hit = (
            payment_service.process_payment(
                idempotency_key,
                payment_request,
            )
        )

        response.status_code = status_code

        if cache_hit:
            response.headers["X-Cache-Hit"] = "true"
        else:
            response.headers["X-Cache-Hit"] = "false"

        return result

    except IdempotencyConflictException as e:
        raise HTTPException(
            status_code=409,
            detail={
                "error": "IDEMPOTENCY_CONFLICT",
                "message": str(e),
                "timestamp": datetime.utcnow().isoformat(),
            },
        )