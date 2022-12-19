"""FastAPIメインクラス."""


from fastapi import Depends, FastAPI
from fastapi.security import OAuth2PasswordRequestForm

# from models.user import UserResponse
# from models.token import TokenResponse
from services.user_service import get_current_active_user, login_for_access_token

app = FastAPI()


@app.post("/token")
def token(
    form_data: OAuth2PasswordRequestForm = Depends(),
):
    """アクセストークン発行エンドポイント."""
    return login_for_access_token(form_data)


@app.get("/users/me/")
def read_users_me(
    current_user: str = Depends(get_current_active_user),
):
    """ユーザ情報確認用エンドポイント."""
    return current_user
