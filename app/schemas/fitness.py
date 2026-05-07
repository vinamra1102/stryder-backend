from typing import List, Optional
from pydantic import BaseModel


class DailySteps(BaseModel):
    date: str
    steps: int


class StepsTodayResponse(BaseModel):
    success: bool
    date: str
    steps: int
    goal: int = 10000
    goal_reached: bool


class WeeklyStepsResponse(BaseModel):
    success: bool
    week_total: int
    daily_average: int
    goal: int = 10000
    days: List[DailySteps]


class StepsHistoryResponse(BaseModel):
    success: bool
    from_date: str
    to_date: str
    total_steps: int
    days: List[DailySteps]
