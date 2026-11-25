import os
from uuid import uuid4

import httpx
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware

USER_URL = os.getenv("USER_SERVICE_URL", "http://user-service:8001")
PRODUCT_URL = os.getenv("PRODUCT_SERVICE_URL", "http://product-service:8002")
ORDER_URL = os.getenv("ORDER_SERVICE_URL", "http://order-service:8003")
PAYMENT_URL = os.getenv("PAYMENT_SERVICE_URL", "http://payment-service:8004")

app = FastAPI(title="MicroFlow API Gateway", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:5173").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def proxy(request: Request, base_url: str, path: str) -> Response:
    request_id = request.headers.get("x-request-id", str(uuid4()))
    async with httpx.AsyncClient(timeout=5.0) as client:
        try:
            upstream = await client.request(
                request.method,
                f"{base_url}{path}",
                params=request.query_params,
                content=await request.body(),
                headers={
                    "content-type": request.headers.get("content-type", "application/json"),
                    "x-request-id": request_id,
                },
            )
        except httpx.RequestError as error:
            raise HTTPException(status_code=503, detail=f"Upstream unavailable: {error}")
    return Response(
        content=upstream.content,
        status_code=upstream.status_code,
        headers={"content-type": upstream.headers.get("content-type", "application/json"), "x-request-id": request_id},
    )


@app.get("/health/live")
def liveness():
    return {"status": "ok"}


@app.get("/health/ready")
async def readiness():
    async with httpx.AsyncClient(timeout=2.0) as client:
        for url in (USER_URL, PRODUCT_URL, ORDER_URL, PAYMENT_URL):
            try:
                response = await client.get(f"{url}/health/ready")
                if response.status_code != 200:
                    return {"status": "not_ready", "dependency": url}
            except httpx.RequestError:
                return {"status": "not_ready", "dependency": url}
    return {"status": "ready"}


@app.api_route("/api/v1/products", methods=["GET"])
async def products(request: Request):
    return await proxy(request, PRODUCT_URL, "/api/v1/products")


@app.api_route("/api/v1/auth/{path:path}", methods=["POST"])
async def auth(request: Request, path: str):
    return await proxy(request, USER_URL, f"/api/v1/auth/{path}")


@app.api_route("/api/v1/orders{path:path}", methods=["GET", "POST"])
async def orders(request: Request, path: str):
    return await proxy(request, ORDER_URL, f"/api/v1/orders{path}")


@app.api_route("/api/v1/payments/{path:path}", methods=["POST"])
async def payments(request: Request, path: str):
    return await proxy(request, PAYMENT_URL, f"/api/v1/payments/{path}")
