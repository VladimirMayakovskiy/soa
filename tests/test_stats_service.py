from datetime import date, timedelta
from unittest.mock import MagicMock, patch

import pytest

import stats_service.service as stats_service
from proto import stats_pb2, stats_pb2_grpc

@pytest.fixture
def fake_ch_client():
    ch = MagicMock()
    ch._client = MagicMock()
    return ch


@pytest.fixture(autouse=True)
def patch_clickhouse(fake_ch_client):
    with patch('stats_service.service.ClickHouseClient', return_value=fake_ch_client):
        yield


@pytest.mark.asyncio
async def test_get_post_stats(fake_ch_client):
    fake_ch_client._client.execute.return_value = [('views', 7), ('likes', 3)]
    svc = stats_service.StatService()

    resp = await svc.GetPostStats(stats_pb2.PostRequest(post_id=55), context=None)
    fake_ch_client._client.execute.assert_called_once()

    assert resp.post_id == 55
    assert resp.views == 7
    assert resp.likes == 3
    assert resp.comments == 0


@pytest.mark.asyncio
@pytest.mark.parametrize("metric_name,grpc_method,sql_metric", [
    ('views', 'GetViewsDynamics', 'views'),
    ('likes', 'GetLikesDynamics', 'likes'),
    ('comments', 'GetCommentsDynamics', 'comments'),
])
async def test_dynamics(metric_name, grpc_method, sql_metric, fake_ch_client):
    today = date.today()
    sample_rows = [
        (today - timedelta(days=0),  1),
        (today - timedelta(days=10), 5),
        (today - timedelta(days=29), 2),
    ]
    fake_ch_client._client.execute.return_value = sample_rows

    svc = stats_service.StatService()
    method = getattr(svc, grpc_method)
    resp = await method(stats_pb2.PostRequest(post_id=99), context=None)

    fake_ch_client._client.execute.assert_called_once()

    assert resp.post_id == 99
    assert len(resp.data) == 30

    day_map = {entry.date: entry.count for entry in resp.data}
    assert day_map[today.isoformat()] == 1
    assert day_map[(today - timedelta(days=10)).isoformat()] == 5
    assert day_map[(today - timedelta(days=29)).isoformat()] == 2
    assert day_map[(today - timedelta(days=1)).isoformat()] == 0


@pytest.mark.asyncio
async def test_clickhouse_error_propagates(fake_ch_client):
    fake_ch_client._client.execute.side_effect = RuntimeError("DB down")
    svc = stats_service.StatService()

    with pytest.raises(RuntimeError) as e:
        await svc.GetPostStats(stats_pb2.PostRequest(post_id=1), context=None)
    assert "DB down" in str(e.value)