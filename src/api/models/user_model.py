"""ユーザモデルのエンティティ、レスポンス情報."""


from pydantic import BaseModel
from sqlalchemy.schema import Column
from sqlalchemy.types import Boolean, String

from api.models.base_model import Base


class UserEntity(Base):
    """ユーザのエンティティクラス."""

    __tablename__ = "user_auth"

    username = Column(String, primary_key=True)
    email = Column(String)
    full_name = Column(String)
    hashed_password = Column(String)
    disabled = Column(Boolean)


class UserResponse(BaseModel):
    """ユーザ情報のレスポンスクラス."""

    username: str
    email: str
    full_name: str
