import importlib.util
import os
from pathlib import Path

from fastapi.testclient import TestClient


ROOT = Path(__file__).resolve().parents[1]


def load_app(service: str):
    path = ROOT / "services" / service / "app" / "main.py"
    os.environ["DATABASE_URL"] = f"sqlite:////tmp/microflow-tests/{service}.db"
    spec = importlib.util.spec_from_file_location(f"{service}_main", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.app


product_app = load_app("product-service")
order_app = load_app("order-service")
payment_app = load_app("payment-service")
user_app = load_app("user-service")


def test_product_catalog_and_health():
    with TestClient(product_app) as client:
        assert client.get("/health/live").status_code == 200
        assert client.get("/health/ready").status_code == 200
        assert len(client.get("/api/v1/products").json()) == 3


def test_checkout_is_idempotent():
    with TestClient(order_app) as client:
        body = {
            "items": [{"product_id": "p1", "quantity": 2}],
            "idempotency_key": "test-key",
        }
        first = client.post("/api/v1/orders/checkout", json=body)
        second = client.post("/api/v1/orders/checkout", json=body)
        assert first.status_code == 201
        assert second.status_code == 201
        assert first.json()["id"] == second.json()["id"]


def test_payment_replays_attempt_outcome():
    with TestClient(payment_app) as client:
        body = {"order_id": "order-1", "attempt_id": "attempt-1", "scenario": "approved"}
        first = client.post("/api/v1/payments/simulate", json=body)
        changed = dict(body, scenario="declined")
        second = client.post("/api/v1/payments/simulate", json=changed)
        assert first.json()["outcome"] == "approved"
        assert second.json()["outcome"] == "approved"


def test_user_registration_and_login():
    with TestClient(user_app) as client:
        email = "portfolio@example.com"
        register = client.post(
            "/api/v1/auth/register",
            json={"email": email, "password": "microflow-test", "name": "Portfolio User"},
        )
        assert register.status_code in (201, 409)
        login = client.post(
            "/api/v1/auth/login",
            json={"email": email, "password": "microflow-test"},
        )
        assert login.status_code == 200
        assert login.json()["token_type"] == "bearer"
