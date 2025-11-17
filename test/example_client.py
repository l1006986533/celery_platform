import requests, time
from pathlib import Path

BASE = "http://127.0.0.1:8000"

# 提交
with Path("../algorithm/race_car.mp4").open("rb") as f:
    r = requests.post(f"{BASE}/track", files={"file": ("race_car.mp4", f, "video/mp4")})
r.raise_for_status()
task_id = r.json()["task_id"]
print("task_id:", task_id)

# 轮询
while True:
    d = requests.get(f"{BASE}/status/{task_id}").json()
    s = d.get("status")
    if s in ("SUCCESS", "FAILURE", "REVOKED"):
        print(d)
        break
    time.sleep(1.5)
