from threading import Lock
from datetime import datetime, timedelta
from typing import Dict, Optional

from models import IdempotencyRecord


class IdempotencyStore:
    def __init__(self):
        # stores all payment records
        self.records: Dict[str, IdempotencyRecord] = {}

        # one lock per idempotency key
        self.locks: Dict[str, Lock] = {}

        # global lock for thread safety
        self.global_lock = Lock()

        # records expire after 24 hours
        self.ttl_hours = 24

    def get_record(self, key: str) -> Optional[IdempotencyRecord]:
        return self.records.get(key)

    def save_record(self, key: str, record: IdempotencyRecord):
        self.records[key] = record

    def get_lock(self, key: str) -> Lock:
        with self.global_lock:
            if key not in self.locks:
                self.locks[key] = Lock()

            return self.locks[key]

    def cleanup_expired_records(self):
        now = datetime.utcnow()

        expired_keys = [
            key
            for key, record in self.records.items()
            if now - record.created_at > timedelta(hours=self.ttl_hours)
        ]

        for key in expired_keys:
            del self.records[key]

            if key in self.locks:
                del self.locks[key]