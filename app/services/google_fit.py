import requests
import time
from datetime import datetime, timedelta, timezone
from typing import Optional
from app.config import DAILY_STEP_GOAL
from app.utils.logger import get_logger

logger = get_logger(__name__)

_AGGREGATE_URL = "https://www.googleapis.com/fitness/v1/users/me/dataset:aggregate"


def _extract_steps_from_bucket(bucket: dict) -> int:
    """Pull step count out of a single Google Fit bucket."""
    try:
        return sum(
            point.get("value", [{}])[0].get("intVal", 0)
            for dataset in bucket.get("dataset", [])
            for point in dataset.get("point", [])
        )
    except (IndexError, KeyError, TypeError):
        return 0


def _aggregate_steps(access_token: str, start_ms: int, end_ms: int) -> Optional[list]:
    """Call Google Fit aggregate API. Returns list of buckets or None on error."""
    body = {
        "aggregateBy": [{"dataTypeName": "com.google.step_count.delta"}],
        "bucketByTime": {"durationMillis": 86400000},
        "startTimeMillis": start_ms,
        "endTimeMillis": end_ms,
    }
    headers = {"Authorization": f"Bearer {access_token}"}
    try:
        res = requests.post(_AGGREGATE_URL, headers=headers, json=body, timeout=10)
    except requests.RequestException as e:
        logger.error(f"Google Fit request failed: {e}")
        return None

    if res.status_code != 200:
        logger.warning(f"Google Fit returned {res.status_code}: {res.text[:200]}")
        return None

    try:
        return res.json().get("bucket", [])
    except ValueError:
        logger.error("Failed to parse Google Fit response as JSON")
        return None


def get_today_steps(access_token: str) -> dict:
    """Return today's step count as a clean dict."""
    now = datetime.now(timezone.utc)
    midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)
    start_ms = int(midnight.timestamp() * 1000)
    end_ms = int(now.timestamp() * 1000)

    buckets = _aggregate_steps(access_token, start_ms, end_ms)
    if buckets is None:
        return {"success": False, "error": "Failed to retrieve step data"}

    steps = sum(_extract_steps_from_bucket(b) for b in buckets)
    today = now.strftime("%Y-%m-%d")

    return {
        "success": True,
        "date": today,
        "steps": steps,
        "goal": DAILY_STEP_GOAL,
        "goal_reached": steps >= DAILY_STEP_GOAL,
    }


def get_weekly_steps(access_token: str) -> dict:
    """Return step counts for the last 7 calendar days (midnight boundaries)."""
    now = datetime.now(timezone.utc)
    today_midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end_ms = int(now.timestamp() * 1000)
    start_ms = int((today_midnight - timedelta(days=6)).timestamp() * 1000)

    buckets = _aggregate_steps(access_token, start_ms, end_ms)
    if buckets is None:
        return {"success": False, "error": "Failed to retrieve step data"}

    days = []
    for bucket in buckets:
        ts_ms = int(bucket.get("startTimeMillis", 0))
        date_str = datetime.fromtimestamp(ts_ms / 1000, tz=timezone.utc).strftime("%Y-%m-%d")
        steps = _extract_steps_from_bucket(bucket)
        days.append({"date": date_str, "steps": steps})

    week_total = sum(d["steps"] for d in days)
    daily_average = week_total // len(days) if days else 0

    return {
        "success": True,
        "week_total": week_total,
        "daily_average": daily_average,
        "goal": DAILY_STEP_GOAL,
        "days": days,
    }


def get_activity_summary(access_token: str) -> dict:
    """Return a dashboard-ready activity summary for the last 7 days."""
    weekly = get_weekly_steps(access_token)
    if not weekly.get("success"):
        return weekly

    days = weekly.get("days", [])

    # Today is the last entry in the calendar-ordered week window
    today_steps = days[-1]["steps"] if days else 0

    best_day = max(days, key=lambda d: d["steps"], default=None) if days else None

    # Count consecutive days (going backwards) that met the daily goal
    streak = 0
    for day in reversed(days):
        if day["steps"] >= DAILY_STEP_GOAL:
            streak += 1
        else:
            break

    return {
        "success": True,
        "today_steps": today_steps,
        "week_total": weekly["week_total"],
        "daily_average": weekly["daily_average"],
        "best_day": best_day,
        "current_streak": streak,
        "goal": DAILY_STEP_GOAL,
        "goal_reached_today": today_steps >= DAILY_STEP_GOAL,
    }


def get_steps_history(access_token: str, from_date: str, to_date: str) -> dict:
    """Return step counts for a custom date range (YYYY-MM-DD strings)."""
    try:
        start_dt = datetime.strptime(from_date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        end_dt = datetime.strptime(to_date, "%Y-%m-%d").replace(tzinfo=timezone.utc) + timedelta(days=1)
    except ValueError:
        return {"success": False, "error": "Invalid date format. Use YYYY-MM-DD"}

    if start_dt > end_dt:
        return {"success": False, "error": "from_date must be before to_date"}

    buckets = _aggregate_steps(
        access_token,
        int(start_dt.timestamp() * 1000),
        int(end_dt.timestamp() * 1000),
    )
    if buckets is None:
        return {"success": False, "error": "Failed to retrieve step data"}

    days = []
    for bucket in buckets:
        ts_ms = int(bucket.get("startTimeMillis", 0))
        date_str = datetime.fromtimestamp(ts_ms / 1000, tz=timezone.utc).strftime("%Y-%m-%d")
        steps = _extract_steps_from_bucket(bucket)
        days.append({"date": date_str, "steps": steps})

    total = sum(d["steps"] for d in days)

    return {
        "success": True,
        "from_date": from_date,
        "to_date": to_date,
        "total_steps": total,
        "days": days,
    }
