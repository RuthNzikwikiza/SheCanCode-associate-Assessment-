import threading
import time

from fastapi import FastAPI

from routes import router, store

app = FastAPI(
    title="IgirePay Idempotency Gateway",
    description="Pay-Once Protocol API",
    version="1.0.0",
)

app.include_router(router)


@app.get("/")
def home():
    return {
        "message": "IgirePay Idempotency Gateway running"
    }


def cleanup_job():
    while True:
        store.cleanup_expired_records()

        time.sleep(3600)


cleanup_thread = threading.Thread(
    target=cleanup_job,
    daemon=True,
)

cleanup_thread.start()