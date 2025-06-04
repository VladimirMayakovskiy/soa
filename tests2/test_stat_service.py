import asyncio
from datetime import datetime, timedelta
from google.protobuf.timestamp_pb2 import Timestamp
from proto import stats_pb2

def run_async(coro):
    return asyncio.get_event_loop().run_until_complete(coro)


def test_get_post_stats_counts(stat_service):
    dummy_rows = [('views', 5), ('likes', 2), ('comments', 3)]
    stat_service._ch._rows_map['PostStats'] = dummy_rows

    req = stats_pb2.PostRequest(post_id=42)
    ctx = None

    resp = run_async(stat_service.GetPostStats(req, ctx))

    assert resp.post_id == 42
    assert resp.views == 5
    assert resp.likes == 2
    assert resp.comments == 3


def test_get_views_dynamics(stat_service):
    today = datetime.utcnow().date()
    start = today - timedelta(days=29)
    end = today

    day2 = start + timedelta(days=2)
    day5 = start + timedelta(days=5)
    dummy_day_rows = [
        (day2, 7),
        (day5, 3)
    ]
    stat_service._ch._rows_map['viewsDynamics'] = dummy_day_rows

    req = stats_pb2.PostRequest(post_id=100)
    ctx = None

    resp= run_async(stat_service.GetViewsDynamics(req, ctx))

    data_list = list(resp.data)
    assert len(data_list) == 30

    result_map = {dc.date: dc.count for dc in data_list}
    assert result_map[day2.isoformat()] == 7
    assert result_map[day5.isoformat()] == 3
    assert result_map[start.isoformat()] == 0
    assert result_map[end.isoformat()] == 0


def test_get_top_posts_and_top(stat_service):
    stat_service._ch._rows_map['TopPosts'] = [(1, 10), (2, 5)]
    stat_service._ch._rows_map['TopUsers'] = [('u1', 8), ('u2', 4)]

    req_posts = stats_pb2.TopRequest(metric=stats_pb2.Metric.Value('VIEWS'))
    ctx = None
    resp_posts = run_async(stat_service.GetTopPosts(req_posts, ctx))
    items = list(resp_posts.items)
    assert len(items) == 2
    assert items[0].post_id == 1
    assert items[0].count == 10
    assert items[1].post_id == 2
    assert items[1].count == 5

    req_users = stats_pb2.TopRequest(metric=stats_pb2.Metric.Value('LIKES'))
    resp_users = run_async(stat_service.GetTopUsers(req_users, ctx))
    u_items = list(resp_users.items)
    assert len(u_items) == 2
    assert u_items[0].user_id == 'u1'
    assert u_items[0].count == 8
    assert u_items[1].user_id == 'u2'
    assert u_items[1].count == 4
