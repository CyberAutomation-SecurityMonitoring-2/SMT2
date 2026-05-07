import requests
import random
import time
import json
from datetime import datetime

TARGET_IP = "192.168.1.10"
BASE_URL = f"http://{TARGET_IP}:5000"
CLIENT_IP = "192.168.1.20"

session = requests.Session()

def log_event(event_type, detail):
    entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "event_type": event_type,
        "client_ip": CLIENT_IP,
        "target": BASE_URL,
        **detail,
    }
    print(json.dumps(entry))
    with open("lab_validation.log", "a") as f:
        f.write(json.dumps(entry) + "\n")

def safe_get(path: str):
    url = f"{BASE_URL}{path}"
    try:
        r = session.get(url, timeout=5)
        log_event("get", {"path": path, "status": r.status_code})
        return r
    except requests.RequestException as e:
        log_event("connection_error", {"path": path, "error": str(e)})
        return None

def safe_post(path: str, payload=None, headers=None):
    url = f"{BASE_URL}{path}"
    try:
        r = session.post(url, json=payload or {}, headers=headers or {}, timeout=5)
        log_event("post", {"path": path, "status": r.status_code})
        return r
    except requests.RequestException as e:
        log_event("connection_error", {"path": path, "error": str(e)})
        return None

def normal_login():
    users = [
        ("player1", "pass123"),
        ("player2", "qwerty"),
        ("admin", "admin123"),
        ("dev_user", "devpass"),
    ]
    username, password = random.choice(users)
    r = safe_post("/login", {"username": username, "password": password})
    if r and r.status_code == 200:
        try:
            token = r.json().get("token", "")
            log_event("login_success", {"username": username})
            return username, token
        except Exception:
            pass
    log_event("login_failed", {"username": username})
    return None, None

def browse_public():
    for path in random.sample(["/health", "/leaderboard"], k=2):
        safe_get(path)
        time.sleep(random.uniform(1, 3))

def use_authenticated_endpoints(username: str, token: str):
    headers = {"Authorization": token}
    safe_get("/profile")
    time.sleep(random.uniform(1, 2))
    safe_post("/score", headers=headers)
    time.sleep(random.uniform(1, 2))
    msg = random.choice([
        "gg",
        "nice match",
        "who is top leaderboard?",
        "lagging a bit today",
        "good game",
    ])
    safe_post("/chat", {"message": msg}, headers=headers)
    log_event("chat_message", {"username": username, "message": msg})

def validation_cycle():
    browse_public()
    username, token = normal_login()
    time.sleep(random.uniform(1, 2))
    if token:
        use_authenticated_endpoints(username, token)
    time.sleep(random.uniform(3, 6))

if __name__ == "__main__":
    print("=" * 60)
    print(" Continuous Catnip Lab Validation Client ")
    print("=" * 60)
    while True:
        validation_cycle()
