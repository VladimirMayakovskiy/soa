#------------------
import pytest
import httpx

@pytest.fixture(scope="function")
def clear_user_fixture():
    async def _clear(pattern: str):
        async with httpx.AsyncClient(base_url="http://user_service:8001") as client:
            resp = await client.delete("/clear", params={"pattern": pattern})
            resp.raise_for_status()
            return resp.json()
    return _clear