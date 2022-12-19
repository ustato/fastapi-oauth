"""データベース操作ユーザリポジトリ."""


from typing import Union

from sqlalchemy.orm import Session

from models.user_model import UserEntity


def get_credentials_by_username(
    db_session: Session, username: str
) -> Union[UserEntity, None]:
    """ユーザ名から登録情報を検索する関数."""
    session = next(db_session[0])
    return session.query(UserEntity).filter_by(username=username).first()
