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


class ActivitySummaryResponse(BaseModel):
    success: bool
    today_steps: int
    week_total: int
    daily_average: int
    best_day: Optional[DailySteps] = None
    current_streak: int
    goal: int = 10000
    goal_reached_today: bool


class MonthlyStepsResponse(BaseModel):
    success: bool
    year: int
    month: int
    total_steps: int
    daily_average: int
    goal: int = 10000
    days: List[DailySteps]
