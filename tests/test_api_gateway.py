from types import SimpleNamespace

import pytest
from fastapi import status
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock

import api_gateway.main as app_module
import api_gateway.grpc_client as grpc_client

from proto import stats_pb2

client = TestClient(app_module.app)

@pytest.fixture(autouse=True)
def patch_grpc_methods():
    grpc_client.get_post_stats = AsyncMock(
        return_value=stats_pb2.PostStats(post_id=123, views=1, likes=2, comments=3)
    )
    grpc_client.get_top_posts = AsyncMock(
        return_value=stats_pb2.TopPostsResponse(items=[
            stats_pb2.PostRank(post_id=1, count=10)
        ])
    )
    yield

def test_proxy_get_post_stats():
    resp = client.get("/stats/123")
    assert resp.status_code == status.HTTP_200_OK
    grpc_client.get_post_stats.assert_awaited_once_with(123)

    data = resp.json()
    assert int(data["post_id"])  == 123
    assert int(data["views"])    == 1
    assert int(data["likes"])    == 2
    assert int(data["comments"]) == 3

def test_top_posts_requires_metric_param():
    resp = client.get("/stats/top/posts")
    assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

def test_top_posts_with_metric():
    resp = client.get("/stats/top/posts?metric=likes")
    assert resp.status_code == status.HTTP_200_OK
    grpc_client.get_top_posts.assert_awaited_once_with('likes')