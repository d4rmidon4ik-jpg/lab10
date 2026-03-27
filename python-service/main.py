import contextlib

import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, field_validator

from client import calculate_via_go, get_item_via_go, ping_go

# Глобальный клиент создаётся один раз при старте и закрывается при остановке
_http_client: httpx.AsyncClient | None = None


@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    global _http_client
    _http_client = httpx.AsyncClient(timeout=5.0)
    yield
    await _http_client.aclose()


app = FastAPI(
    title="Python Gateway Service",
    description=(
        "FastAPI-сервис, который проксирует запросы к Go-сервису (Gin). "
        "Задания 4 и 8 из ЛР №10."
    ),
    version="1.0.0",
    lifespan=lifespan,
)


def get_client() -> httpx.AsyncClient:
    if _http_client is None:
        raise RuntimeError("HTTP client is not initialized")
    return _http_client


class CalculateRequest(BaseModel):
    a: float
    b: float
    op: str

    @field_validator("op")
    @classmethod
    def validate_op(cls, v: str) -> str:
        allowed = {"add", "sub", "mul", "div"}
        if v not in allowed:
            raise ValueError(f"op must be one of {allowed}")
        return v


@app.get("/health", summary="Healthcheck этого сервиса")
async def health() -> dict:
    return {"status": "ok", "service": "python-gateway"}


@app.get(
    "/go/ping",
    summary="Проксирует /ping к Go-сервису",
    tags=["proxy"],
)
async def proxy_ping() -> dict:
    try:
        return await ping_go(get_client())
    except httpx.HTTPError as e:
        raise HTTPException(status_code=502, detail=f"Go service unavailable: {e}")


@app.post(
    "/go/calculate",
    summary="Проксирует /calculate к Go-сервису",
    tags=["proxy"],
)
async def proxy_calculate(req: CalculateRequest) -> dict:
    try:
        return await calculate_via_go(get_client(), req.a, req.b, req.op)
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail=e.response.json(),
        )
    except httpx.HTTPError as e:
        raise HTTPException(status_code=502, detail=f"Go service unavailable: {e}")


@app.get(
    "/go/items/{item_id}",
    summary="Проксирует /items/:id к Go-сервису",
    tags=["proxy"],
)
async def proxy_item(item_id: int) -> dict:
    try:
        return await get_item_via_go(get_client(), item_id)
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail=e.response.json(),
        )
    except httpx.HTTPError as e:
        raise HTTPException(status_code=502, detail=f"Go service unavailable: {e}")
