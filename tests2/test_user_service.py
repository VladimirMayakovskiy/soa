from datetime import datetime

from user_service.models import User
from user_service.utils import hash_password, verify_password
from fastapi import status


def test_signup_success(client, db_session):
    payload = {
        "username": "alice",
        "email": "alice@example.com",
        "password": "strongpwd"
    }
    resp = client.post("/signup", json=payload)
    assert resp.status_code == 200, f"{resp.status_code}: {resp.text}"

    data = resp.json()
    assert data["username"] == "alice"
    assert data["email"] == "alice@example.com"
    assert "id" in data
    assert "created_at" in data and "updated_at" in data

    db_session.expire_all()
    user_in_db = db_session.query(User).filter(User.id == data["id"]).first()
    assert user_in_db is not None
    assert user_in_db.email == "alice@example.com"
    assert user_in_db.password != "strongpwd"
    assert verify_password("strongpwd", user_in_db.password)


def test_signup_conflict_email(client, db_session):
    bob = User(username="bob", email="bob@example.com", password=hash_password("123456"))
    db_session.add(bob)
    db_session.commit()

    payload = {
        "username": "bobby",
        "email": "bob@example.com",
        "password": "anotherpwd"
    }
    resp = client.post("/signup", json=payload)
    assert resp.status_code == 409
    assert resp.json()["detail"] == "Email already register"

def test_login_and_get_profile(client, db_session):
    raw_pwd = "secret123"
    hashed = hash_password(raw_pwd)
    user = User(
        username="bob",
        email="bob@example.com",
        password=hashed
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    login_payload = {"username": "bob", "email": "bob@example.com", "password": raw_pwd}
    resp_login = client.post("/login", json=login_payload)
    assert resp_login.status_code == 200, f"{resp_login.status_code}: {resp_login.text}"
    token = resp_login.json().get("access_token")
    assert token is not None
    assert isinstance(token, str) and len(token) > 0

    cookies = resp_login.cookies
    assert "user_access_token" in cookies
    assert cookies.get("user_access_token") == token

    resp_profile = client.get("/profile")
    assert resp_profile.status_code == 200
    prof = resp_profile.json()
    assert prof["username"] == "bob"
    assert prof["email"] == "bob@example.com"
    assert prof["id"] == user.id


def test_update_profile_unauthorized_and_success(client, db_session):
    update_payload = {"first_name": "Charlie", "last_name": "Brown"}
    resp = client.put("/update", json=update_payload)
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    #----------------

    raw_pwd = "mypassword"
    hashed = hash_password(raw_pwd)
    user = User(username="dave", email="dave@example.com", password=hashed)
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    resp_login = client.post("/login", json={"username": "dave", "email": "dave@example.com", "password": raw_pwd})
    assert resp_login.status_code == 200

    new_data = {
        "first_name": "David",
        "last_name": "Jones",
        "birth_date": "1990-05-10",
        "phone": "+1234567890"
    }
    resp_update = client.put("/update", json=new_data)
    assert resp_update.status_code == 200

    upd = resp_update.json()
    assert upd["first_name"] == "David"
    assert upd["last_name"] == "Jones"
    assert upd["phone"] == "+1234567890"

    created_at = datetime.fromisoformat(upd["created_at"])
    updated_at = datetime.fromisoformat(upd["updated_at"])
    assert updated_at >= created_at
