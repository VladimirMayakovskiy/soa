import os

# os.environ["TEST"] = "true"
# os.environ["TEST_DATABASE_URL"] = "sqlite:///./test_db.sqlite"

import sys
import types

import httpx
import pytest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from user_service.main import app
from user_service import db as db_module, kafka_client
from user_service import config as config_module
from user_service.models import Base
from user_service import utils

from user_service import db as db_module, utils
from user_service.models import Base
from user_service.main import app

from post_service import db as post_db_module
from post_service.models import Base as PostBase

@pytest.fixture(scope="function", autouse=True)
def create_sqlite_tables():
    Base.metadata.create_all(bind=db_module.engine)
    yield
    Base.metadata.drop_all(bind=db_module.engine)

@pytest.fixture(scope="function")
def db_session():
    # session = TestingSessionLocal()
    session = db_module.SessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(scope="function")
def client(monkeypatch, db_session):
    def override_get_db():
        db = db_module.SessionLocal()
        try:
            yield db
        finally:
            db.close()
    app.dependency_overrides[ db_module.get_db ] = override_get_db

    class DummyProducer:
        async def send_event(self, topic: str, event: dict):
            return

    import user_service.kafka_client as real_kafka_mod
    monkeypatch.setattr(real_kafka_mod, "get_producer", lambda: DummyProducer())

    import user_service.main as main_mod
    monkeypatch.setattr(main_mod, "get_producer", lambda: DummyProducer())
    dummy_kafka_mod = types.ModuleType("kafka_client")
    dummy_kafka_mod.get_producer = lambda: DummyProducer()
    sys.modules["kafka_client"] = dummy_kafka_mod

    def fake_get_auth_data():
        secret = "testsecret123"
        return {"private_key": secret, "public_key": secret, "algorithm": "HS256"}

    monkeypatch.setattr(utils, "get_auth_data", fake_get_auth_data)
    monkeypatch.setattr(config_module, "get_auth_data", fake_get_auth_data)

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


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

    import post_service.kafka_client as real_kafka_mod
    monkeypatch.setattr(real_kafka_mod, "get_producer", lambda: DummyProducer())

    from post_service.service import PostService
    svc = PostService()
    return svc


# ─────────────────────────────────────────────────────────────────────────────

@pytest.fixture(scope="function")
def stat_service(monkeypatch):
    class DummyClient:
        def __init__(self, rows_map=None):
            self._client = self
            self._rows_map = rows_map or {}

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

    import stats_service.service as svc_mod
    monkeypatch.setattr(svc_mod, "ClickHouseClient", lambda: DummyClient())

    from stats_service.service import StatService
    svc = StatService()
    return svc

#------------------------

import stats_service.kafka_client as kafka_mod

class DummyClickHouse:
    def __init__(self):
        self.inserted = []
        self._client = self

    def execute(self, *args, **kwargs):
        return []

    def insert_event(self, event_date, post_id, user_id, metric):
        self.inserted.append((event_date, post_id, user_id, metric))

@pytest.fixture(scope="function")
def dummy_clickhouse(monkeypatch):
    orig_ch = kafka_mod.ClickHouseClient

    monkeypatch.setattr(kafka_mod, "ClickHouseClient", lambda: DummyClickHouse())
    yield DummyClickHouse

    monkeypatch.setattr(kafka_mod, "ClickHouseClient", orig_ch)

