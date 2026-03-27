import httpx

GO_SERVICE_URL = "http://localhost:8080"


async def ping_go(client: httpx.AsyncClient) -> dict:
    response = await client.get(f"{GO_SERVICE_URL}/ping")
    response.raise_for_status()
    return response.json()


async def calculate_via_go(
    client: httpx.AsyncClient,
    a: float,
    b: float,
    op: str,
) -> dict:
    response = await client.post(
        f"{GO_SERVICE_URL}/calculate",
        json={"a": a, "b": b, "op": op},
    )
    response.raise_for_status()
    return response.json()


async def get_item_via_go(client: httpx.AsyncClient, item_id: int) -> dict:
    response = await client.get(f"{GO_SERVICE_URL}/items/{item_id}")
    response.raise_for_status()
    return response.json()
