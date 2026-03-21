from pydantic import BaseModel


class TokenVerifyRequest(BaseModel):
    id_token: str


class TokenVerifyResponse(BaseModel):
    uid: str
    email: str | None
    display_name: str | None
