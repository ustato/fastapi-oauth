"""データベースの接続情報."""


from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

engine = create_engine(
    "sqlite:///test.sqlite3",
    echo=True,
    future=True,
    encoding="utf-8",
)

SessionTest = sessionmaker(
    bind=engine,
    # autocommit=False,
    autoflush=True,
)


def get_test_database() -> Session:
    """データベースセッション取得関数."""
    db_session = SessionTest()

    try:
        yield db_session
    finally:
        db_session.close()
