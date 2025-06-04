import os

import sys
import types

import pytest

from fastapi.testclient import TestClient

from user_service.main import app
from user_service import db as user_db_module
from user_service import config as user_config_module
from user_service.models import Base as UserBase
from user_service import utils

from post_service import db as post_db_module
from post_service.models import Base as PostBase

#-------------------------------------------------------------------

@pytest.fixture(scope="function", autouse=True)
def create_sqlite_tables_user():
    UserBase.metadata.create_all(bind=user_db_module.engine)
    yield
    UserBase.metadata.drop_all(bind=user_db_module.engine)
    try:
        os.remove("test_db.sqlite")
    except FileNotFoundError:
        pass

@pytest.fixture(scope="function")
def db_session_user():
    session = user_db_module.SessionLocal()
    try:
        yield session
    finally:
        session.close()

@pytest.fixture(scope="function")
def user_service(monkeypatch, db_session_user):
    def override_get_db():
        db = user_db_module.SessionLocal()
        try:
            yield db
        finally:
            db.close()
    app.dependency_overrides[ user_db_module.get_db ] = override_get_db

    class DummyProducer:
        async def send_event(self, topic: str, event: dict):
            return

    import user_service.kafka_client as user_service_kafka_client
    monkeypatch.setattr(user_service_kafka_client, "get_producer", lambda: DummyProducer())

    dummy_kafka_mod = types.ModuleType("kafka_client")
    dummy_kafka_mod.get_producer = lambda: DummyProducer()
    sys.modules["kafka_client"] = dummy_kafka_mod

    def fake_get_auth_data():
        secret = "testsecret123"
        return {"private_key": secret, "public_key": secret, "algorithm": "HS256"}

    monkeypatch.setattr(utils, "get_auth_data", fake_get_auth_data)
    monkeypatch.setattr(user_config_module, "get_auth_data", fake_get_auth_data)

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()

#-----------------------------------------------


@pytest.fixture(scope="function", autouse=True)
def create_sqlite_tables_post():
    PostBase.metadata.create_all(bind=post_db_module.engine)
    yield
    PostBase.metadata.drop_all(bind=post_db_module.engine)
    try:
        os.remove("test_db.sqlite")
    except FileNotFoundError:
        pass

@pytest.fixture(scope="function")
def db_session_post():
    session = post_db_module.SessionLocal()
    try:
        yield session
    finally:
        session.close()

@pytest.fixture(scope="function")
def post_service(monkeypatch):
    class DummyProducer:
        async def send_event(self, topic: str, event: dict):
            return

    import post_service.kafka_client as post_service_kafka_client
    monkeypatch.setattr(post_service_kafka_client, "get_producer", lambda: DummyProducer())

    from post_service.service import PostService
    return PostService()


# ─────────────────────────────────────────────────────────────────────────────

class DummyClickHouse:
    def __init__(self, rows_map=None):
        self._client = self
        self._rows_map = rows_map or {}
        self.inserted = []

    def execute(self, query, params):
        q = query.strip().lower()
        if 'from stats_' in q and 'group by metric' in q:
            return self._rows_map.get('PostStats', [])
        if 'and metric =' in q and 'between' in q:
            key = params.get('m', '')
            return self._rows_map.get(f'{key}Dynamics', [])
        if 'group by post_id' in q and 'order by cnt desc' in q:
            return self._rows_map.get('TopPosts', [])
        if 'group by user_id' in q and 'order by cnt desc' in q:
            return self._rows_map.get('TopUsers', [])
        return []

    def insert_event(self, event_date, post_id, user_id, metric):
        self.inserted.append((event_date, post_id, user_id, metric))

@pytest.fixture(scope="function")
def stat_service(monkeypatch):
    import stats_service.service as svc
    monkeypatch.setattr(svc, "ClickHouseClient", lambda: DummyClickHouse())

    from stats_service.service import StatService
    return StatService()

#----------------------------------------------------------------------------

@pytest.fixture(scope="function")
def dummy_clickhouse(monkeypatch):
    import stats_service.kafka_client as stats_service_kafka_client

    monkeypatch.setattr(stats_service_kafka_client, "ClickHouseClient", lambda: DummyClickHouse())
    yield DummyClickHouse

