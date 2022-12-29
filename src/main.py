"""FastAPIメインクラス."""


from fastapi import Depends, FastAPI, UploadFile

from api.models.token_model import TokenResponse
from api.models.user_model import UserResponse
from api.services import file_service, user_service

app = FastAPI()


@app.post("/token", response_model=TokenResponse)
def generate_token(
    token: TokenResponse = Depends(user_service.login_for_access_token),
):
    """アクセストークン発行API."""
    return token


@app.get("/users/me", response_model=UserResponse)
def get_users_me(
    current_user: UserResponse = Depends(user_service.get_current_active_user),
):
    """ユーザ情報確認用API."""
    return current_user


@app.post("/statistics")
def csv_statistics(
    upload_file: UploadFile,
    current_user: UserResponse = Depends(user_service.get_current_active_user),
):
    """アップロードされたCSVのそれぞれのカラムの統計量を算出して、結果をJSONで返すAPI."""
    return file_service.aggregate_csv(upload_file.file)
