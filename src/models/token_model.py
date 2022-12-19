"""トークンモデルのレスポンスクラス."""


from pydantic import BaseModel


class TokenResponse(BaseModel):
    """トークン情報のレスポンスクラス."""

    access_token: str
    token_type: str
