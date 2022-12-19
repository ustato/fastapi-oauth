"""初回マイグレーション用スクリプト."""


from api.database import engine, get_database
from api.models.base_model import Base
from api.models.user_model import UserEntity

Base.metadata.create_all(bind=engine)


inital_user = UserEntity(
    username="johndoe",
    full_name="John Doe",
    email="johndoe@example.com",
    hashed_password="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
    disabled=False,
)


session = next(get_database())
print(dir(session))
session.add(inital_user)
session.commit()
