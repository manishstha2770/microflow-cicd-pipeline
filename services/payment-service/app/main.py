import os
import sqlite3
from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel

DATABASE = os.getenv("DATABASE_URL", "sqlite:///data/payment.db")


def db_path() -> Path:
    path = DATABASE.removeprefix("sqlite:///")
    result = Path(path)
    result.parent.mkdir(parents=True, exist_ok=True)
    return result


def database() -> sqlite3.Connection:
    connection = sqlite3.connect(db_path())
    connection.row_factory = sqlite3.Row
    return connection


class PaymentRequest(BaseModel):
    order_id: str
    attempt_id: str
    scenario: str = "approved"


app = FastAPI(title="MicroFlow Payment Service", version="1.0.0")


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
            "CREATE TABLE IF NOT EXISTS payments "
            "(attempt_id TEXT PRIMARY KEY, order_id TEXT NOT NULL, outcome TEXT NOT NULL)"
        )


@app.get("/health/live")
def liveness():
    return {"status": "ok"}


@app.get("/health/ready")
def readiness():
    with database() as connection:
        connection.execute("SELECT 1").fetchone()
    return {"status": "ready"}


@app.post("/api/v1/payments/simulate")
def simulate(body: PaymentRequest):
    if not body.order_id or not body.attempt_id:
        raise HTTPException(status_code=400, detail="order_id and attempt_id are required")
    outcome = "approved" if body.scenario.lower() != "declined" else "declined"
    with database() as connection:
        existing = connection.execute(
            "SELECT outcome FROM payments WHERE attempt_id = ?", (body.attempt_id,)
        ).fetchone()
        if existing:
            outcome = existing["outcome"]
        else:
            connection.execute(
                "INSERT INTO payments(attempt_id, order_id, outcome) VALUES (?, ?, ?)",
                (body.attempt_id, body.order_id, outcome),
            )
    return {"attempt_id": body.attempt_id, "order_id": body.order_id, "outcome": outcome}
