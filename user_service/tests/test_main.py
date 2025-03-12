import pytest
from fastapi.testclient import TestClient

from ..main import app
from ..db import SessionLocal
from ..utils import hash_password
from ..models import User


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


@pytest.fixture(scope="function", autouse=True)
def clear_db():
    db = SessionLocal()
    db.query(User).filter(User.email.like('%@test.example.com')).delete(synchronize_session=False)
    db.commit()
    db.close()
    yield


@pytest.fixture(scope='function')
def client():
    return TestClient(app)


@pytest.fixture
def test_user():
    db = SessionLocal()
    user = User(
        username="testuser",
        email="testuser@test.example.com",
        password=hash_password("testpassword")
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    db.close()
    return user


def test_signup(client):
    response = client.post("/signup", json={
        "username": "newuser",
        "email": "newuser@test.example.com",
        "password": "newpassword"
    })
    assert response.status_code == 200, response.text
    data = response.json()
    check_user(data, username="newuser", email="newuser@test.example.com")


def test_signup_duplicate_email(client, test_user):
    response = client.post("/signup", json={
        "username": "newuser",
        "email": test_user.email,
        "password": "newpassword"
    })
    assert response.status_code == 409
    data = response.json()
    assert data["detail"] == "Email already register"


def test_login_success(client, test_user):
    response = client.post("/login", json={
        "username": test_user.username,
        "email": test_user.email,
        "password": "testpassword"
    })
    print(response)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data


def test_login_failure(client, test_user):
    response = client.post("/login", json={
        "username": test_user.username,
        "email": test_user.email,
        "password": "wrongpassword"
    })
    assert response.status_code == 401
    data = response.json()
    assert data["detail"] == "Invalid user credentials"


def test_get_profile_unauthorized(client):
    response = client.get("/profile")
    assert response.status_code == 401
    data = response.json()
    assert data["detail"] == "Token not found"


def test_profile_and_update(client, test_user):
    login_response = client.post("/login", json={
        "username": test_user.username,
        "email": test_user.email,
        "password": "testpassword"
    })
    assert login_response.status_code == 200
    token = login_response.cookies.get("user_access_token")
    assert token is not None

    profile_response = client.get("/profile", cookies={"user_access_token": token})
    assert profile_response.status_code == 200
    profile_data = profile_response.json()
    check_user(
        profile_data,
        username=test_user.username,
        email=test_user.email,
    )

    update_response = client.put("/update", json={
        "first_name": "John",
        "last_name": "Doe",
        "phone": "+123456789"
    }, cookies={"user_access_token": token})
    assert update_response.status_code == 200
    updated_data = update_response.json()

    check_user(
        updated_data,
        username=test_user.username,
        email=test_user.email,
        first_name="John",
        last_name="Doe",
        phone="+123456789"
    )
