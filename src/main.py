"""FastAPIメインクラス."""


from fastapi import Depends, FastAPI
from fastapi.security import OAuth2PasswordRequestForm

from api.models.token_model import TokenResponse
from api.models.user_model import UserResponse
from api.services.user_service import get_current_active_user, login_for_access_token

app = FastAPI()


@app.post("/token", response_model=TokenResponse)
def token(
    form_data: OAuth2PasswordRequestForm = Depends(),
):
    """アクセストークン発行エンドポイント."""
    return login_for_access_token(form_data)


@app.get("/users/me/", response_model=UserResponse)
def read_users_me(
    current_user: UserResponse = Depends(get_current_active_user),
):
    """ユーザ情報確認用エンドポイント."""
    return current_user
