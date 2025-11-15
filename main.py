import hashlib
import time
import requests
import os


APP_KEY = os.getenv("APP_KEY")
APP_SECRET = os.getenv("APP_SECRET")
DEVICE_SN = os.getenv("DEVICE_SN")

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

API_URL = "https://api.ecoflow.com/api/cloud/open/getDeviceQuota"


def make_signature(secret, timestamp):
    raw = f"{secret}{timestamp}"
    return hashlib.sha256(raw.encode()).hexdigest()


def query_device_quota():
    timestamp = int(time.time() * 1000)

    headers = {
        "Content-Type": "application/json",
        "X-App-Key": APP_KEY,
        "X-Timestamp": str(timestamp),
        "X-Sign": make_signature(APP_SECRET, timestamp)
    }

    body = {"sn": DEVICE_SN}

    response = requests.post(API_URL, headers=headers, json=body)
    response.raise_for_status()

    return response.json()


def send_telegram(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": TELEGRAM_CHAT_ID, "text": text})


def main():
    try:
        data = query_device_quota()

        if data.get("code") != 0:
            send_telegram(f"❗ Помилка EcoFlow API: {data}")
            return

        soc = data["data"].get("soc")
        send_telegram(f"🔋 Поточний SOC: {soc}%")

    except Exception as e:
        send_telegram(f"❗️ Помилка моніторингу: {e}")


if __name__ == "__main__":
    main()
