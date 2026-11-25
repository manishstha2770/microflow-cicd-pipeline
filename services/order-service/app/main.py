import os
import sqlite3
from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel

DATABASE = os.getenv("DATABASE_URL", "sqlite:///data/order.db")


def db_path() -> Path:
    path = DATABASE.removeprefix("sqlite:///")
    result = Path(path)
    result.parent.mkdir(parents=True, exist_ok=True)
    return result


def database() -> sqlite3.Connection:
    connection = sqlite3.connect(db_path())
    connection.row_factory = sqlite3.Row
    return connection


class CheckoutItem(BaseModel):
    product_id: str
    quantity: int


class CheckoutRequest(BaseModel):
    items: list[CheckoutItem]
    idempotency_key: str


app = FastAPI(title="MicroFlow Order Service", version="1.0.0")


@app.middleware("http")
async def request_context(request: Request, call_next):
    request_id = request.headers.get("x-request-id", str(uuid4()))
    response = await call_next(request)
    response.headers["x-request-id"] = request_id
    return response


@app.on_event("startup")
def startup() -> None:
    with database() as connection:
        connection.execute(
            "CREATE TABLE IF NOT EXISTS orders "
            "(id TEXT PRIMARY KEY, idempotency_key TEXT UNIQUE, status TEXT, total_cents INTEGER)"
        )


@app.get("/health/live")
def liveness():
    return {"status": "ok"}


@app.get("/health/ready")
def readiness():
    with database() as connection:
        connection.execute("SELECT 1").fetchone()
    return {"status": "ready"}


@app.post("/api/v1/orders/checkout", status_code=201)
def checkout(body: CheckoutRequest):
    if not body.items or any(item.quantity < 1 for item in body.items):
        raise HTTPException(status_code=400, detail="At least one valid item is required")
    order_id = str(uuid4())
    total_cents = sum(item.quantity * 100 for item in body.items)
    with database() as connection:
        try:
            connection.execute(
                "INSERT INTO orders(id, idempotency_key, status, total_cents) VALUES (?, ?, ?, ?)",
                (order_id, body.idempotency_key, "pending_payment", total_cents),
            )
        except sqlite3.IntegrityError:
            existing = connection.execute(
                "SELECT id, status, total_cents FROM orders WHERE idempotency_key = ?",
                (body.idempotency_key,),
            ).fetchone()
            return {"id": existing["id"], "status": existing["status"], "total_cents": existing["total_cents"]}
    return {"id": order_id, "status": "pending_payment", "total_cents": total_cents}


@app.get("/api/v1/orders")
def list_orders():
    with database() as connection:
        rows = connection.execute("SELECT id, status, total_cents FROM orders").fetchall()
    return [dict(row) for row in rows]
