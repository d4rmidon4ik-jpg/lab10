import pytest
from fastapi.testclient import TestClient
from main import CalculateRequest, app


# TestClient используется как контекстный менеджер — это запускает lifespan,
# который инициализирует _http_client перед тестами и закрывает его после.
@pytest.fixture(scope="session")
def client():
    with TestClient(app, raise_server_exceptions=True) as c:
        yield c


# ---------------------------------------------------------------------------
# /health  — не зависит от Go
# ---------------------------------------------------------------------------
def test_health_status(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


# ---------------------------------------------------------------------------
# /go/ping
# ---------------------------------------------------------------------------
def test_proxy_ping_ok(client):
    resp = client.get("/go/ping")
    assert resp.status_code == 200
    data = resp.json()
    assert data["message"] == "pong"
    assert data["status"] == "ok"


# ---------------------------------------------------------------------------
# /go/calculate
# ---------------------------------------------------------------------------
def test_proxy_calculate_add(client):
    resp = client.post("/go/calculate", json={"a": 10, "b": 3, "op": "add"})
    assert resp.status_code == 200
    assert resp.json()["result"] == pytest.approx(13.0)


def test_proxy_calculate_sub(client):
    resp = client.post("/go/calculate", json={"a": 10, "b": 3, "op": "sub"})
    assert resp.status_code == 200
    assert resp.json()["result"] == pytest.approx(7.0)


def test_proxy_calculate_mul(client):
    resp = client.post("/go/calculate", json={"a": 4, "b": 5, "op": "mul"})
    assert resp.status_code == 200
    assert resp.json()["result"] == pytest.approx(20.0)


def test_proxy_calculate_div(client):
    resp = client.post("/go/calculate", json={"a": 10, "b": 2, "op": "div"})
    assert resp.status_code == 200
    assert resp.json()["result"] == pytest.approx(5.0)


def test_proxy_calculate_division_by_zero(client):
    resp = client.post("/go/calculate", json={"a": 5, "b": 0, "op": "div"})
    assert resp.status_code == 422


def test_proxy_calculate_invalid_op(client):
    # Pydantic отклоняет "pow" до обращения к Go
    resp = client.post("/go/calculate", json={"a": 5, "b": 2, "op": "pow"})
    assert resp.status_code == 422


def test_proxy_calculate_missing_fields(client):
    resp = client.post("/go/calculate", json={"a": 5})
    assert resp.status_code == 422


def test_proxy_calculate_negative_numbers(client):
    resp = client.post("/go/calculate", json={"a": -4, "b": -2, "op": "mul"})
    assert resp.status_code == 200
    assert resp.json()["result"] == pytest.approx(8.0)


# ---------------------------------------------------------------------------
# /go/items/:id
# ---------------------------------------------------------------------------
def test_proxy_item_valid(client):
    resp = client.get("/go/items/7")
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == 7
    assert isinstance(data["name"], str)


def test_proxy_item_not_found(client):
    resp = client.get("/go/items/-1")
    assert resp.status_code == 404


def test_proxy_item_zero(client):
    resp = client.get("/go/items/0")
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# Pydantic-валидация — чистый unit-тест, Go не нужен
# ---------------------------------------------------------------------------
def test_calculate_request_model_rejects_invalid_op():
    with pytest.raises(Exception):
        CalculateRequest(a=1, b=2, op="mod")
