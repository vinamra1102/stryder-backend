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

    res = requests.post(url, headers=headers, json=body)
    return res.json()