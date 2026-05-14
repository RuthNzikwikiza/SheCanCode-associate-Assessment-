# Idempotency Gateway — IgirePay Pay-Once System

## Problem Statement

Payment systems often suffer from duplicate charges when network retries happen.  
This service ensures that a payment request is processed **exactly once**, even if the client sends it multiple times due to timeouts or retries.

---

## Architecture

```text
Client
  ↓
POST /process-payment (Idempotency-Key header)
  ↓
FastAPI Routes (API Layer)
  ↓
Payment Service (Business Logic)
  ↓
Idempotency Store (In-Memory Dictionary)
  ↓
Decision:
  ├── New Key → Process payment (simulate 2s delay)
  ├── Same Key + Same Payload → Return cached response
  └── Same Key + Different Payload → Return 409 Conflict
```

---

## How Idempotency Works

- Client sends a request with an `Idempotency-Key`
- Server checks if the key already exists

### Case 1: New Key
- Process payment
- Simulate 2-second delay
- Store response

### Case 2: Same Key + Same Payload
- Return cached response (no reprocessing)
- Add header: `X-Cache-Hit: true`

### Case 3: Same Key + Different Payload
- Reject request
- Return `409 Conflict`
- Message: "Idempotency key already used for a different request body."

---

## API Documentation

### POST /process-payment

#### Headers
```
Idempotency-Key: unique-string
```

#### Request Body
```json
{
  "amount": 100,
  "currency": "USD"
}
```

---

## Success Response

```json
{
  "status": "SUCCESS",
  "message": "Charged 100 USD",
  "idempotency_key": "unique-string"
}
```

---

## Duplicate Request Response

Same response as first request (no reprocessing)

Header:
```
X-Cache-Hit: true
```

---

## Conflict Response

```json
{
  "detail": "Idempotency key already used for a different request body."
}
```

Status Code:
```
409 Conflict
```

---

## How to Run

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

Open in browser:

```
http://127.0.0.1:8000/docs
```

---

## Choice Feature

### TTL Expiry System

Automatically removes old idempotency keys after a fixed time.

### Why this matters:
- Prevents memory leaks
- Improves scalability
- Simulates real production caching systems (like Redis TTL)

---

## Final Architecture Summary

```text
Client
  ↓
POST /process-payment
  ↓
FastAPI Routes
  ↓
Payment Service
  ↓
Idempotency Store
  ↓
Decision:
  ├── New Key → Process payment
  ├── Same Key + Same Payload → Return cached response
  └── Same Key + Different Payload → Reject (409)
  
```