from typing import Optional
from pydantic import BaseModel, Field


class UserSettings(BaseModel):
    daily_step_goal: int = Field(default=10000, ge=1000, le=100000)
    notifications_enabled: bool = True
    units: str = Field(default="metric", pattern="^(metric|imperial)$")
    theme: str = Field(default="system", pattern="^(light|dark|system)$")


class UserSettingsResponse(BaseModel):
    success: bool
    settings: UserSettings


class UserProfileResponse(BaseModel):
    success: bool
    sub: str
    email: str
    name: str
    picture: Optional[str] = None
