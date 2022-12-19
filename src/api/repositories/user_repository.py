"""ユーザに関するデータベース操作を提供するリポジトリ層."""


from typing import Union

from sqlalchemy.orm import Session

from api.models.user_model import UserEntity


def get_credentials_by_username(
    db_session: Session, username: str
) -> Union[UserEntity, None]:
    """ユーザ名から登録情報を検索する関数."""
    return db_session.query(UserEntity).filter_by(username=username).first()
