import os
import sqlite3
from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel

DATABASE = os.getenv("DATABASE_URL", "sqlite:///data/product.db")


def db_path() -> Path:
    path = DATABASE.removeprefix("sqlite:///")
    result = Path(path)
    result.parent.mkdir(parents=True, exist_ok=True)
    return result


def database() -> sqlite3.Connection:
    connection = sqlite3.connect(db_path())
    connection.row_factory = sqlite3.Row
    return connection


class ReserveRequest(BaseModel):
    items: list[dict]
    operation_id: str


app = FastAPI(title="MicroFlow Product Service", version="1.0.0")


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
            "CREATE TABLE IF NOT EXISTS products "
            "(id TEXT PRIMARY KEY, name TEXT NOT NULL, description TEXT, price_cents INTEGER, stock INTEGER)"
        )


@app.get("/health/live")
def liveness():
    return {"status": "ok"}


@app.get("/health/ready")
def readiness():
    with database() as connection:
        connection.execute("SELECT 1").fetchone()
    return {"status": "ready"}


@app.get("/api/v1/products")
def list_products():
    return [
        {"id": "p1", "name": "MicroFlow Hoodie", "description": "Cloud-native everyday hoodie", "price_cents": 4800, "stock": 25},
        {"id": "p2", "name": "DevOps Mug", "description": "Ceramic mug for deployment days", "price_cents": 1800, "stock": 50},
        {"id": "p3", "name": "Kubernetes Sticker", "description": "A durable cluster-ready decal", "price_cents": 600, "stock": 100},
    ]


@app.post("/api/v1/inventory/reserve")
def reserve(body: ReserveRequest):
    if not body.items:
        raise HTTPException(status_code=400, detail="At least one item is required")
    return {"operation_id": body.operation_id, "status": "reserved"}
