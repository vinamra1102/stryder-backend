import requests
import time
from app.utils.logger import get_logger

logger = get_logger(__name__)

_AGGREGATE_URL = "https://www.googleapis.com/fitness/v1/users/me/dataset:aggregate"


def get_today_steps(access_token: str) -> dict:
    now = int(time.time() * 1000)
    start = now - 86400000  # last 24 hours

    body = {
        "aggregateBy": [{"dataTypeName": "com.google.step_count.delta"}],
        "bucketByTime": {"durationMillis": 86400000},
        "startTimeMillis": start,
        "endTimeMillis": now,
    }
    headers = {"Authorization": f"Bearer {access_token}"}

    try:
        res = requests.post(_AGGREGATE_URL, headers=headers, json=body, timeout=10)
    except requests.RequestException as e:
        logger.error(f"Google Fit request failed: {e}")
        return {"error": "Failed to reach Google Fit API", "details": str(e)}

    if res.status_code != 200:
        logger.warning(f"Google Fit returned {res.status_code}: {res.text[:200]}")
        return {"error": "Google Fit API error", "details": res.text}

    try:
        return res.json()
    except ValueError:
        logger.error("Failed to parse Google Fit response as JSON")
        return {"error": "Invalid response from Google Fit API"}
