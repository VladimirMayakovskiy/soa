import respx
import httpx
import pytest
from fastapi.testclient import TestClient
from ..main import app
from ..config import USER_SERVICE_URL

client = TestClient(app)


@respx.mock
def test_proxy_get():
    test_path = "test-endpoint"
    expected_response = {"message": "success"}
    respx.get(f"{USER_SERVICE_URL}/{test_path}").mock(
        return_value=httpx.Response(200, json=expected_response)
    )

    response = client.get(f"/{test_path}")
    assert response.status_code == 200
    data = response.json()
    assert data == expected_response


@respx.mock
def test_proxy_post():
    test_path = "test-endpoint"
    expected_response = {"message": "created"}
    respx.post(f"{USER_SERVICE_URL}/{test_path}").mock(
        return_value=httpx.Response(201, json=expected_response)
    )

    response = client.post(f"/{test_path}", json={"key": "value"})
    assert response.status_code == 201
    data = response.json()
    assert data == expected_response
