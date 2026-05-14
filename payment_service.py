import uuid
import time

from datetime import datetime

from models import (
    PaymentRequest,
    PaymentResponse,
    IdempotencyRecord,
    ProcessingStatus,
)

from store import IdempotencyStore


class IdempotencyConflictException(Exception):
    pass


class PaymentService:
    def __init__(self, store: IdempotencyStore):
        self.store = store

    def process_payment(
        self,
        idempotency_key: str,
        payment_request: PaymentRequest,
    ):
        request_fingerprint = payment_request.to_fingerprint()

        lock = self.store.get_lock(idempotency_key)

        with lock:

            existing_record = self.store.get_record(idempotency_key)
       
            if existing_record:

                if (
                    existing_record.request_fingerprint
                    != request_fingerprint
                ):
                    raise IdempotencyConflictException(
                        "Idempotency key already used with different payload"
                    )

                return (
                    existing_record.response,
                    existing_record.http_status_code,
                    True,
                )

            time.sleep(2)

            transaction_id = str(uuid.uuid4())

            response = PaymentResponse(
                status="SUCCESS",
                message=f"Payment of {payment_request.amount} {payment_request.currency} processed successfully",
                transaction_id=transaction_id,
                idempotency_key=idempotency_key,
                processed_at=datetime.utcnow().isoformat(),
            )

            record = IdempotencyRecord(
                request_fingerprint=request_fingerprint,
                status=ProcessingStatus.COMPLETED,
                created_at=datetime.utcnow(),
                response=response,
                http_status_code=201,
            )

            self.store.save_record(idempotency_key, record)

            return response, 201, False