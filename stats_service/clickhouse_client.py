import os
from clickhouse_driver import Client
from stats_service.config import settings


class ClickHouseClient:
    def __init__(self):
        self._client = Client(host=settings.CLICKHOUSE_HOST, port=settings.CLICKHOUSE_PORT, user=settings.CLICKHOUSE_USER, password=settings.CLICKHOUSE_PASSWORD)
        self._init()

    def _init(self):
        self._client.execute('''
        create table if not exists stats_ (
            event_date Date,
            post_id UInt32,
            user_id String,
            metric String
        )
        engine = MergeTree()
        partition by event_date
        order by (post_id, metric)
        ''')

    def insert_event(self, event_date, post_id, user_id, metric):
        self._client.execute(
            'insert into stats_ (event_date, post_id, user_id, metric) values',
            [(event_date, post_id, user_id, metric)]
        )
