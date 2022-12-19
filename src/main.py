"""FastAPIメインクラス."""


from fastapi import Depends, FastAPI

from api.models.token_model import TokenResponse
from api.models.user_model import UserResponse
from api.services.user_service import get_current_active_user, login_for_access_token

app = FastAPI()


@app.post("/token", response_model=TokenResponse)
def generate_token(
    token: TokenResponse = Depends(login_for_access_token),
):
    """アクセストークン発行エンドポイント."""
    return token


@app.get("/users/me/", response_model=UserResponse)
def get_users_me(
    current_user: UserResponse = Depends(get_current_active_user),
):
    """ユーザ情報確認用エンドポイント."""
    return current_user
