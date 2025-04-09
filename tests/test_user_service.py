import os
import pytest
import httpx

USER_SERVICE_URL = os.environ.get("USER_SERVICE_URL", "http://user_service:8001")

client = httpx.Client(base_url=USER_SERVICE_URL)

def check_user(
        data,
        *,
        username: str,
        email: str,
        first_name: str = None,
        last_name: str = None,
        birth_date: str = None,
        phone: str = None
):
    assert data["username"] == username
    assert data["email"] == email
    if first_name:
        assert data["first_name"] == first_name
    if last_name:
        assert data["last_name"] == last_name
    if birth_date:
        assert data["birth_date"] == birth_date
    if phone:
        assert data["phone"] == phone


@pytest.fixture(autouse=True)
def cleanup():
    yield

    response = client.delete("/clear", params={"pattern": "@test.example.com"})
    assert response.status_code == 200, response.text


@pytest.fixture()
def test_user():
    response = client.post("/signup", json={
        "username": "testuser",
        "email": f"testuser@test.example.com",
        "password": "testpassword"
    })
    assert response.status_code == 200, response.text
    return response.json()


def test_signup():
    response = client.post("/signup", json={
        "username": "newuser",
        "email": "newuser@test.example.com",
        "password": "newpassword"
    })
    assert response.status_code == 200, response.text
    data = response.json()
    check_user(data, username="newuser", email="newuser@test.example.com")


def test_signup_duplicate_email(test_user):
    response = client.post("/signup", json={
        "username": "newuser",
        "email": test_user["email"],
        "password": "newpassword"
    })
    assert response.status_code == 409
    data = response.json()
    assert data["detail"] == "Email already register"


def test_login_success(test_user):
    response = client.post("/login", json={
        "username": test_user["username"],
        "email": test_user["email"],
        "password": "testpassword"
    })
    assert response.status_code == 200
    assert "user_access_token" in response.cookies


def test_login_failure(test_user):
    response = client.post("/login", json={
        "username": test_user["username"],
        "email": test_user["email"],
        "password": "wrongpassword"
    })
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid user credentials"


def test_get_profile_unauthorized():
    client.cookies.clear()
    response = client.get("/profile")
    assert response.status_code == 401
    assert response.json()["detail"] == "Token not found"


def test_profile_and_update(test_user):
    login_response = client.post("/login", json={
        "username": test_user["username"],
        "email": test_user["email"],
        "password": "testpassword"
    })
    assert login_response.status_code == 200
    token = login_response.cookies.get("user_access_token")
    assert token is not None

    profile_response = client.get("/profile", cookies={"user_access_token": token})
    assert profile_response.status_code == 200, profile_response.text
    check_user(
        profile_response.json(),
        username=test_user["username"],
        email=test_user["email"],
    )

    update_response = client.put("/update", json={
        "first_name": "John",
        "last_name": "Doe",
        "phone": "+123456789"
    }, cookies={"user_access_token": token})
    assert update_response.status_code == 200, update_response.text

    check_user(
        update_response.json(),
        username=test_user["username"],
        email=test_user["email"],
        first_name="John",
        last_name="Doe",
        phone="+123456789"
    )
