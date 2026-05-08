import os
import pytest
from unittest.mock import MagicMock, patch

os.environ.setdefault("POSTGRES_HOST", "localhost")
os.environ.setdefault("POSTGRES_USER", "test")
os.environ.setdefault("POSTGRES_PASSWORD", "test")
os.environ.setdefault("POSTGRES_DB", "testdb")
os.environ.setdefault("REDIS_HOST", "localhost")

from app import app  # noqa: E402


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


@patch("app.get_db_connection")
@patch("app.r")
def test_health_ok(mock_redis, mock_db, client):
    mock_redis.ping.return_value = True
    mock_db.return_value = MagicMock()
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json()["status"] == "ok"


@patch("app.r")
def test_health_redis_down(mock_redis, client):
    import redis as redis_lib
    mock_redis.ping.side_effect = redis_lib.RedisError("connection refused")
    response = client.get("/health")
    assert response.status_code == 503


@patch("app.get_db_connection")
@patch("app.r")
def test_get_messages_returns_list(mock_redis, mock_db, client):
    mock_conn = MagicMock()
    mock_cur = MagicMock()
    mock_cur.fetchall.return_value = [
        {"id": 1, "author": "alice", "content": "hello", "created_at": "2024-01-01"}
    ]
    mock_conn.cursor.return_value = mock_cur
    mock_db.return_value = mock_conn
    response = client.get("/api/messages")
    assert response.status_code == 200
    assert isinstance(response.get_json(), list)


def test_add_message_missing_content(client):
    response = client.post("/api/messages", json={"author": "alice"})
    assert response.status_code == 400


def test_add_message_no_body(client):
    response = client.post(
        "/api/messages",
        data="",
        content_type="application/json",
    )
    assert response.status_code == 400


@patch("app.get_db_connection")
def test_add_message_success(mock_db, client):
    mock_conn = MagicMock()
    mock_cur = MagicMock()
    mock_cur.fetchone.return_value = {
        "id": 1,
        "author": "alice",
        "content": "hello",
        "created_at": "2024-01-01",
    }
    mock_conn.cursor.return_value = mock_cur
    mock_db.return_value = mock_conn
    response = client.post(
        "/api/messages",
        json={"author": "alice", "content": "hello"},
    )
    assert response.status_code == 201
