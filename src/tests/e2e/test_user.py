"""ユーザログインテスト."""


import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from sqlalchemy_utils import create_database, drop_database

from api.database import get_database
from api.models.base_model import Base
from api.models.user_model import UserEntity
from api.services.user_service import decode_access_token
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
        hashed_password="fakehashedsecret1",
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

    return TestClient(app)


def test_get_users_me_NR001(client):
    """ユーザー情報取得API 正常系テスト."""

    def _decode_access_token_override():
        return {"sub": "johndoe", "exp": 9876543210}

    app.dependency_overrides[decode_access_token] = _decode_access_token_override

    response = client.get("/users/me", headers={"Authorization": "dummy_token"})
    assert response.status_code == 200
    assert response.json() == {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
    }


def test_get_users_me_ABR001(client):
    """
    ユーザー情報取得API 異常系テスト.

    トークン認識不能.
    """
    app.dependency_overrides[decode_access_token] = decode_access_token

    response = client.get("/users/me", headers={"Authorization": "Beare"})
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}


def test_get_users_me_ABR002(client):
    """
    ユーザー情報取得API 異常系テスト.

    トークン不正.
    """
    app.dependency_overrides[decode_access_token] = decode_access_token

    response = client.get("/users/me", headers={"Authorization": "Bearer"})
    assert response.status_code == 401
    assert response.json() == {"detail": "Could not validate credentials"}


def test_get_users_me_ABR003(client):
    """
    ユーザー情報取得API 異常系テスト.

    存在しないユーザー指定.
    """

    def _decode_access_token_override():
        return {"sub": "jo", "exp": 9876543210}

    app.dependency_overrides[decode_access_token] = _decode_access_token_override

    response = client.get("/users/me", headers={"Authorization": "dummy_token"})
    assert response.status_code == 401
    assert response.json() == {"detail": "Could not find user"}


def test_get_users_me_ABR004(client):
    """
    ユーザー情報取得API 異常系テスト.

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
            hashed_password="fakehashedsecret2",
            disabled=True,
        )
    )

    response = client.get("/users/me", headers={"Authorization": "dummy_token"})
    assert response.status_code == 400
    assert response.json() == {"detail": "Inactive user"}
