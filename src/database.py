"""データベースの接続情報."""


from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

try:
    engine = create_engine(
        "sqlite:///db.sqlite3",
        echo=True,
        future=True,
        encoding="utf-8",
        pool_recycle=3600,
        pool_size=0,
        max_overflow=-1,
    )
except TypeError:
    engine = create_engine(
        "sqlite:///db.sqlite3",
        echo=True,
        future=True,
        encoding="utf-8",
    )

SessionLocal = sessionmaker(
    bind=engine,
    # autocommit=False,
    # autoflush=False
)


def get_database() -> Session:
    """データベースセッション取得関数."""
    db_session = SessionLocal()

    try:
        yield db_session
    finally:
        db_session.close()
