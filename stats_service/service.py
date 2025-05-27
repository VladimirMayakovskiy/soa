from datetime import datetime, timedelta

from proto import stats_pb2, stats_pb2_grpc

import os
if os.environ.get("TEST", "false") == "true":
    ClickHouseClient = None
else:
    from stats_service.clickhouse_client import ClickHouseClient


class StatService(stats_pb2_grpc.StatServiceServicer):
    def __init__(self):
        self._ch = ClickHouseClient()
    async def GetPostStats(self, request, context):
        post_id = request.post_id
        rows = self._ch._client.execute(
            '''
            select metric, count()
            from stats_
            where post_id = %(pid)s
            group by metric
            ''', {'pid': post_id}
        )
        stats = {}
        for metric, cnt in rows:
            stats[metric] = cnt
        return stats_pb2.PostStats(
            post_id=post_id,
            views=stats.get('views', 0),
            likes=stats.get('likes', 0),
            comments=stats.get('comments', 0),
        )

    async def _get_dynamics(self, post_id, metric):
        date = datetime.utcnow().date()
        start = date - timedelta(days=29)
        rows = self._ch._client.execute(
            '''
            select event_date, count()
            from stats_
            where post_id = %(pid)s
                and metric = %(m)s
                and event_date between %(start)s and %(end)s
            group by event_date
            order by event_date
            ''', {'pid': post_id, 'm': metric, 'start': start, 'end': date}
        )
        day_map = {start + timedelta(days=i): 0 for i in range(30)}
        for day, cnt in rows:
            day_map[day] = cnt
        return [stats_pb2.DateCount(date=day.isoformat(), count=cnt) for day, cnt in day_map.items()]

    async def GetViewsDynamics(self, request, context):
        data = await self._get_dynamics(request.post_id, 'views')
        return stats_pb2.PostDynamics(post_id=request.post_id, data=data)

    async def GetLikesDynamics(self, request, context):
        data = await self._get_dynamics(request.post_id, 'likes')
        return stats_pb2.PostDynamics(post_id=request.post_id, data=data)

    async def GetCommentsDynamics(self, request, context):
        data = await self._get_dynamics(request.post_id, 'comments')
        return stats_pb2.PostDynamics(post_id=request.post_id, data=data)

    async def GetTopPosts(self, request, context):
        metric = stats_pb2.Metric.Name(request.metric).lower()
        rows = self._ch._client.execute(
            '''
            select post_id, count() as cnt
            from stats_
            where metric = %(m)s
            group by post_id
            order by cnt desc
            limit 10
            ''', {'m': metric}
        )
        items = [stats_pb2.PostRank(post_id=pid, count=cnt) for pid, cnt in rows]
        return stats_pb2.TopPostsResponse(items=items)

    async def GetTopUsers(self, request, context):
        metric = stats_pb2.Metric.Name(request.metric).lower()
        rows = self._ch._client.execute(
            '''
            select user_id, count() as cnt
            from stats_
            where metric = %(m)s
            group by user_id
            order by cnt desc
            limit 10
            ''', {'m': metric}
        )
        items = [stats_pb2.UserRank(user_id=uid, count=cnt) for uid, cnt in rows]
        return stats_pb2.TopUsersResponse(items=items)
