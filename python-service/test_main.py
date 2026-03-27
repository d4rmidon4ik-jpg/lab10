import json

import httpx
import pytest
from fastapi.testclient import TestClient

import main as app_module
from main import CalculateRequest, app


class MockTransport(httpx.AsyncBaseTransport):
    """Перехватывает запросы к Go-сервису и возвращает фиктивные ответы."""

    async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
        path = request.url.path

        if path == "/ping":
            return httpx.Response(200, json={"message": "pong", "status": "ok"})

        if path == "/calculate":
            body = json.loads(request.content)
            a, b, op = body["a"], body["b"], body["op"]
            if op == "div" and b == 0:
                return httpx.Response(422, json={"error": "division by zero"})
            results = {"add": a + b, "sub": a - b, "mul": a * b, "div": a / b}
            return httpx.Response(200, json={"result": results[op], "op": op})

        if path.startswith("/items/"):
            item_id = int(path.split("/")[-1])
            if item_id <= 0:
                return httpx.Response(404, json={"error": "item not found"})
            return httpx.Response(200, json={"id": item_id, "name": f"Item {item_id}"})

        return httpx.Response(404, json={"error": "not found"})


@pytest.fixture(autouse=True)
def inject_mock_client():
    app_module._http_client = httpx.AsyncClient(transport=MockTransport())
    yield


client = TestClient(app)


# --- /health ---

def test_health_status():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


# --- /go/ping ---

def test_proxy_ping_ok():
    resp = client.get("/go/ping")
    assert resp.status_code == 200
    data = resp.json()
    assert data["message"] == "pong"
    assert data["status"] == "ok"


# --- /go/calculate ---

def test_proxy_calculate_add():
    resp = client.post("/go/calculate", json={"a": 10, "b": 3, "op": "add"})
    assert resp.status_code == 200
    assert resp.json()["result"] == 13.0


def test_proxy_calculate_sub():
    resp = client.post("/go/calculate", json={"a": 10, "b": 3, "op": "sub"})
    assert resp.status_code == 200
    assert resp.json()["result"] == 7.0


def test_proxy_calculate_mul():
    resp = client.post("/go/calculate", json={"a": 4, "b": 5, "op": "mul"})
    assert resp.status_code == 200
    assert resp.json()["result"] == 20.0


def test_proxy_calculate_div():
    resp = client.post("/go/calculate", json={"a": 10, "b": 2, "op": "div"})
    assert resp.status_code == 200
    assert resp.json()["result"] == 5.0


def test_proxy_calculate_division_by_zero():
    resp = client.post("/go/calculate", json={"a": 5, "b": 0, "op": "div"})
    assert resp.status_code == 422


def test_proxy_calculate_invalid_op():
    # Pydantic отклоняет на уровне FastAPI, до Go не доходит
    resp = client.post("/go/calculate", json={"a": 5, "b": 2, "op": "pow"})
    assert resp.status_code == 422


def test_proxy_calculate_missing_fields():
    resp = client.post("/go/calculate", json={"a": 5})
    assert resp.status_code == 422


def test_proxy_calculate_negative_numbers():
    resp = client.post("/go/calculate", json={"a": -4, "b": -2, "op": "mul"})
    assert resp.status_code == 200
    assert resp.json()["result"] == 8.0


# --- /go/items/:id ---

def test_proxy_item_valid():
    resp = client.get("/go/items/7")
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == 7
    assert isinstance(data["name"], str)


def test_proxy_item_not_found():
    resp = client.get("/go/items/-1")
    assert resp.status_code == 404


def test_proxy_item_zero():
    resp = client.get("/go/items/0")
    assert resp.status_code == 404


# --- Pydantic validation ---

def test_calculate_request_model_rejects_invalid_op():
    with pytest.raises(Exception):
        CalculateRequest(a=1, b=2, op="mod")
