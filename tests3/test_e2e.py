import pytest
import asyncio
import httpx
from datetime import datetime, timedelta

from proto import stats_pb2, stats_pb2_grpc

def run_async(coro):
    return asyncio.get_event_loop().run_until_complete(coro)


@pytest.mark.asyncio
async def test_e2e_view_like_comment_flow(clear_user_fixture):
    await clear_user_fixture("e2euser")

    base = "http://api_gateway:8000"

    async with httpx.AsyncClient(base_url=base) as client:
        signup_resp = await client.post(
            "/user/signup",
            json={"username": "e2euser", "email": "e2e@example.com", "password": "strongpwd"}
        )
        assert signup_resp.status_code == 200

        login_resp = await client.post(
            "/user/login",
            json={"username": "e2euser", "email": "e2e@example.com", "password": "strongpwd"}
        )
        assert login_resp.status_code == 200


        create_resp = await client.post(
            "/post",
            json={"title": "E2E", "description": "Test post", "private": False, "tags": ["ww", "e2e"]},
        )
        assert create_resp.status_code == 200
        post_data = create_resp.json()
        post_id = post_data["id"]
        assert post_data["title"] == "E2E"


        view_resp = await client.post(f"/post/{post_id}/view")
        assert view_resp.status_code == 200


        like_resp = await client.post(f"/post/{post_id}/like")
        assert like_resp.status_code == 200

        comment_resp = await client.post(
            f"/post/{post_id}/comment",
            json={"text": "Nice"}
        )
        assert comment_resp.status_code == 200
        comment_data = comment_resp.json()
        assert comment_data["post_id"] == post_id
        assert comment_data["text"] == "Nice"


    async with httpx.AsyncClient(base_url=base) as client:

        stats_resp = await client.get(f"/stats/{post_id}")
        assert stats_resp.status_code == 200
        stats_data = stats_resp.json()
        assert stats_data["post_id"] == post_id
        assert int(stats_data["views"]) == 1
        assert int(stats_data["likes"]) == 1
        assert int(stats_data["comments"]) == 1


        dyn_resp = await client.get(f"/stats/{post_id}/views")
        assert dyn_resp.status_code == 200
        dyn_data = dyn_resp.json().get("data", [])
        assert isinstance(dyn_data, list) and len(dyn_data) == 30

        last = dyn_data[-1]
        today_str = datetime.utcnow().date().isoformat()
        assert last["date"] == today_str
        assert int(last["count"]) == 1

    await clear_user_fixture("e2euser")

@pytest.mark.asyncio
async def test_e2e_private_post_visibility_and_update(clear_user_fixture):
    await clear_user_fixture("userA_e2e")
    await clear_user_fixture("userB_e2e")

    base = "http://api_gateway:8000"

    async with httpx.AsyncClient(base_url=base) as client:

        resp = await client.post("/user/signup", json={
            "username": "userA_e2e",
            "email":    "userA_e2e@example.com",
            "password": "passwordA"
        })
        assert resp.status_code == 200


        resp = await client.post("/user/login", json={
            "username": "userA_e2e",
            "email":    "userA_e2e@example.com",
            "password": "passwordA"
        })
        assert resp.status_code == 200


        create_resp = await client.post("/post", json={
            "title":       "Private Post",
            "description": "Только для A",
            "private":     True,
            "tags":        ["private"]
        })
        assert create_resp.status_code == 200
        post_id = create_resp.json()["id"]


    async with httpx.AsyncClient(base_url=base) as client:

        resp = await client.post("/user/signup", json={
            "username": "userB_e2e",
            "email":    "userB_e2e@example.com",
            "password": "passwordB"
        })
        assert resp.status_code == 200


        resp = await client.post("/user/login", json={
            "username": "userB_e2e",
            "email":    "userB_e2e@example.com",
            "password": "passwordB"
        })
        assert resp.status_code == 200


        get_priv = await client.get(f"/post/{post_id}")
        assert get_priv.status_code != 200


        list_priv = await client.get("/post", params={"page": 1, "limit": post_id})
        assert list_priv.status_code == 200
        posts = list_priv.json().get("post", [])
        assert all(p["id"] != post_id for p in posts)


    async with httpx.AsyncClient(base_url=base) as client:

        resp = await client.post("/user/login", json={
            "username": "userA_e2e",
            "email":    "userA_e2e@example.com",
            "password": "passwordA"
        })
        assert resp.status_code == 200


        upd_resp = await client.put(f"/post/{post_id}", json={
            "title":       "Now Public",
            "description": "Все",
            "private":     False,
            "tags":        ["public"]
        })
        assert upd_resp.status_code == 200
        updated = upd_resp.json()
        assert updated["private"] is False
        assert updated["title"] == "Now Public"


    async with httpx.AsyncClient(base_url=base) as client:

        resp = await client.post("/user/login", json={
            "username": "userB_e2e",
            "email":    "userB_e2e@example.com",
            "password": "passwordB"
        })
        assert resp.status_code == 200


        list_pub = await client.get("/post", params={"page": 1, "limit": post_id})
        assert list_pub.status_code == 200
        posts = list_pub.json().get("post", [])
        assert any(p["id"] == post_id for p in posts), [p["id"] for p in posts] + [post_id]


        get_pub = await client.get(f"/post/{post_id}")
        assert get_pub.status_code == 200, f"{get_pub}"
        p = get_pub.json()
        assert p["title"] == "Now Public"
        assert p["private"] is False


        view_resp = await client.post(f"/post/{post_id}/view")
        assert view_resp.status_code == 200


    await asyncio.sleep(5)
    async with httpx.AsyncClient(base_url=base) as client:
        stats_resp = await client.get(f"/stats/{post_id}")
        assert stats_resp.status_code == 200
        stats_data = stats_resp.json()

        for key in ("views", "likes", "comments"):
            stats_data[key] = int(stats_data[key])
        assert stats_data["views"] == 1
        assert stats_data["likes"] == 0
        assert stats_data["comments"] == 0


    await clear_user_fixture("userA_e2e")
    await clear_user_fixture("userB_e2e")


@pytest.mark.asyncio
async def test_e2e_multiple_posts_and_aggregate_stats_via_gateway(clear_user_fixture):
    await clear_user_fixture("e2euser")
    base = "http://api_gateway:8000"


    async with httpx.AsyncClient(base_url=base) as client:
        signup = await client.post(
            "/user/signup",
            json={"username": "e2euser", "email": "e2e@example.com", "password": "strongpwd"}
        )
        assert signup.status_code == 200
        login = await client.post(
            "/user/login",
            json={"username": "e2euser", "email": "e2e@example.com", "password": "strongpwd"}
        )
        assert login.status_code == 200


        resp1 = await client.post(
            "/post",
            json={"title": "GW Post1", "description": "Desc1", "private": False, "tags": ["gw"]}
        )
        assert resp1.status_code == 200
        pid1 = resp1.json()["id"]

        resp2 = await client.post(
            "/post",
            json={"title": "GW Post2", "description": "Desc2", "private": False, "tags": ["gw"]}
        )
        assert resp2.status_code == 200
        pid2 = resp2.json()["id"]

        for _ in range(2):
            v = await client.post(f"/post/{pid1}/view")
            assert v.status_code == 200
        l1 = await client.post(f"/post/{pid1}/like")
        assert l1.status_code == 200
        c1 = await client.post(f"/post/{pid1}/comment", json={"text": "comment1"})
        assert c1.status_code == 200


        v2 = await client.post(f"/post/{pid2}/view")
        assert v2.status_code == 200
        for _ in range(2):
            l2 = await client.post(f"/post/{pid2}/like")
            assert l2.status_code == 200
        for _ in range(2):
            c2 = await client.post(f"/post/{pid2}/comment", json={"text": "comment2"})
            assert c2.status_code == 200




    async with httpx.AsyncClient(base_url=base) as client:

        stats1 = await client.get(f"/stats/{pid1}")
        sd1 = stats1.json()
        assert int(sd1["views"]) == 2
        assert int(sd1["likes"]) == 1
        assert int(sd1["comments"]) == 1


        stats2 = await client.get(f"/stats/{pid2}")
        sd2 = stats2.json()
        assert int(sd2["views"]) == 1
        assert int(sd2["likes"]) == 2
        assert int(sd2["comments"]) == 2

    await clear_user_fixture("e2euser")
