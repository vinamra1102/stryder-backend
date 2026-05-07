from typing import Optional
from pydantic import BaseModel


class UserProfile(BaseModel):
    sub: str
    email: str
    name: str
    picture: Optional[str] = None


class TokenResponse(BaseModel):
    success: bool
    access_token: str
    token_type: str = "bearer"


class MeResponse(BaseModel):
    success: bool
    user: UserProfile
