import hashlib
import hmac
import json
import os
import sqlite3
import time
from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, EmailStr

DATABASE = os.getenv("DATABASE_URL", "sqlite:///data/user.db")
JWT_SECRET = os.getenv("JWT_SECRET", "local-development-secret")


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    name: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


def db_path() -> Path:
    path = DATABASE.removeprefix("sqlite:///")
    result = Path(path)
    result.parent.mkdir(parents=True, exist_ok=True)
    return result


def database() -> sqlite3.Connection:
    connection = sqlite3.connect(db_path())
    connection.row_factory = sqlite3.Row
    return connection


def password_hash(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def encode_segment(value: dict) -> str:
    import base64

    raw = json.dumps(value, separators=(",", ":")).encode()
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode()


def create_token(subject: str) -> str:
    header = encode_segment({"alg": "HS256", "typ": "JWT"})
    payload = encode_segment({
        "sub": subject,
        "exp": int(time.time()) + 3600,
        "iat": int(time.time()),
    })
    signature = hmac.new(JWT_SECRET.encode(), f"{header}.{payload}".encode(), hashlib.sha256)
    return f"{header}.{payload}.{signature.digest().hex()}"


app = FastAPI(title="MicroFlow User Service", version="1.0.0")


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
            "CREATE TABLE IF NOT EXISTS users "
            "(id TEXT PRIMARY KEY, email TEXT UNIQUE NOT NULL, name TEXT NOT NULL, password_hash TEXT NOT NULL)"
        )


@app.get("/health/live")
def liveness():
    return {"status": "ok"}


@app.get("/health/ready")
def readiness():
    with database() as connection:
        connection.execute("SELECT 1").fetchone()
    return {"status": "ready"}


@app.post("/api/v1/auth/register", status_code=201)
def register(body: RegisterRequest):
    try:
        with database() as connection:
            connection.execute(
                "INSERT INTO users(id, email, name, password_hash) VALUES (?, ?, ?, ?)",
                (str(uuid4()), body.email.lower(), body.name, password_hash(body.password)),
            )
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=409, detail="Email is already registered")
    return {"status": "registered"}


@app.post("/api/v1/auth/login")
def login(body: LoginRequest):
    with database() as connection:
        user = connection.execute(
            "SELECT id, password_hash FROM users WHERE email = ?", (body.email.lower(),)
        ).fetchone()
    if not user or not hmac.compare_digest(user["password_hash"], password_hash(body.password)):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"access_token": create_token(user["id"]), "token_type": "bearer"}
