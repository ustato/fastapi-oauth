"""ファイル集計APIテスト."""


import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from sqlalchemy_utils import create_database, drop_database

from api.database import get_database
from api.models.base_model import Base
from api.models.user_model import UserEntity
from api.services.user_service import (
    decode_access_token,
    get_callable_create_access_token,
)
from main import app
from tests.database import engine, get_test_database


@pytest.fixture
def db_fixture() -> Session:
    """データベース初期化処理."""
    Base.metadata.create_all(bind=engine)
    create_database(engine.url)

    inital_user = UserEntity(
        username="johndoe",
        full_name="John Doe",
        email="johndoe@example.com",
        hashed_password="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
        disabled=False,
    )

    db_session = next(get_test_database())
    db_session.add(inital_user)
    db_session.commit()

    yield db_session

    drop_database(engine.url)


@pytest.fixture
def client(db_fixture) -> TestClient:
    """テスト用クライアント."""

    def _get_database_override():
        return db_fixture

    app.dependency_overrides[get_database] = _get_database_override
    app.dependency_overrides[decode_access_token] = decode_access_token
    app.dependency_overrides[
        get_callable_create_access_token
    ] = get_callable_create_access_token

    return TestClient(app)


def test_csv_statistics_NR001(client):
    """CSV統計量算出API 正常系テスト."""

    def _decode_access_token_override():
        return {"sub": "johndoe", "exp": 9876543210}

    app.dependency_overrides[decode_access_token] = _decode_access_token_override

    with open("src/tests/resources/csv/dummy.csv", "rb") as f:
        response = client.post(
            "/statistics",
            headers={
                "Authorization": "dummy_token",
                "accept": "application/json",
            },
            files={"upload_file": f},
        )
    assert response.status_code == 200
    assert response.json() == {
        "age": {"sum": 52174, "variance": 362.8906146146146},
        "income": {"sum": 5217400000, "variance": 3628906146146.146},
    }


def test_csv_statistics_ABR001(client):
    """
    CSV統計量算出API 異常系テスト.

    トークン認識不能.
    """
    with open("src/tests/resources/csv/dummy.csv", "rb") as f:
        response = client.post(
            "/statistics",
            headers={
                "Authorization": "Beare",
                "accept": "application/json",
            },
            files={"upload_file": f},
        )
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}


def test_csv_statistics_ABR002(client):
    """
    CSV統計量算出API 異常系テスト.

    トークン不正.
    """
    with open("src/tests/resources/csv/dummy.csv", "rb") as f:
        response = client.post(
            "/statistics",
            headers={
                "Authorization": "Bearer",
                "accept": "application/json",
            },
            files={"upload_file": f},
        )
    assert response.status_code == 401
    assert response.json() == {"detail": "Could not validate credentials"}


def test_csv_statistics_ABR003(client):
    """
    CSV統計量算出API 異常系テスト.

    存在しないユーザー指定.
    """

    def _decode_access_token_override():
        return {"sub": "jo", "exp": 9876543210}

    app.dependency_overrides[decode_access_token] = _decode_access_token_override

    with open("src/tests/resources/csv/dummy.csv", "rb") as f:
        response = client.post(
            "/statistics",
            headers={
                "Authorization": "dummy_token",
                "accept": "application/json",
            },
            files={"upload_file": f},
        )
    assert response.status_code == 401
    assert response.json() == {"detail": "Could not find user"}


def test_csv_statistics_ABR004(client):
    """
    CSV統計量算出API 異常系テスト.

    非アクティブユーザー指定.
    """

    def _decode_access_token_override():
        return {"sub": "alice", "exp": 9876543210}

    app.dependency_overrides[decode_access_token] = _decode_access_token_override

    db_session = app.dependency_overrides[get_database]()
    db_session.add(
        UserEntity(
            username="alice",
            full_name="Alice Wonderson",
            email="alice@example.com",
            hashed_password="fakehashedsecret",
            disabled=True,
        )
    )

    with open("src/tests/resources/csv/dummy.csv", "rb") as f:
        response = client.post(
            "/statistics",
            headers={
                "Authorization": "dummy_token",
                "accept": "application/json",
            },
            files={"upload_file": f},
        )
    assert response.status_code == 400
    assert response.json() == {"detail": "Inactive user"}
