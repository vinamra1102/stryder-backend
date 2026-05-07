import requests
import time

def get_today_steps(access_token):
    url = "https://www.googleapis.com/fitness/v1/users/me/dataset:aggregate"

    now = int(time.time() * 1000)
    start = now - 86400000

    body = {
        "aggregateBy": [{
            "dataTypeName": "com.google.step_count.delta"
        }],
        "bucketByTime": {"durationMillis": 86400000},
        "startTimeMillis": start,
        "endTimeMillis": now
    }

    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    try:
        res = requests.post(url, headers=headers, json=body, timeout=10)
    except requests.RequestException as e:
        return {"error": "Failed to fetch steps", "details": str(e)}

    if res.status_code != 200:
        return {"error": "Failed to fetch steps", "details": res.text}

    try:
        return res.json()
    except ValueError:
        return {"error": "Invalid response from Google Fit API"}