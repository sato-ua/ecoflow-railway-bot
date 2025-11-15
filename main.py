import hashlib
import hmac
import json
import time
import requests
import os

APP_KEY = os.getenv("APP_KEY")
APP_SECRET = os.getenv("APP_SECRET")
DEVICE_SN = os.getenv("DEVICE_SN")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

API_URL = "https://api.ecoflow.com/iot-open/sign/device/queryDeviceQuota"


def make_signature(params, app_secret):
    sorted_params = sorted(params.items())
    data = "".join(f"{k}{v}" for k, v in sorted_params)
    signature = hmac.new(
        app_secret.encode("utf-8"),
        data.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()
    return signature


def query_device_quota():
    timestamp = int(time.time() * 1000)

    params = {
        "appKey": APP_KEY,
        "sn": DEVICE_SN,
        "timestamp": timestamp
    }

    signature = make_signature(params, APP_SECRET)
    params["sign"] = signature

    headers = {"Content-Type": "application/json"}

    response = requests.post(API_URL, headers=headers, json=params)
    response.raise_for_status()

    return response.json()


def send_telegram(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": text}
    requests.post(url, json=payload)


def main():
    try:
        data = query_device_quota()

        if data.get("code") != "0":
            send_telegram(f"❗️ Помилка від EcoFlow: {data}")
            return

        quota = data["data"]
        soc = quota.get("soc")

        send_telegram(f"🔋 SOC: {soc}%")

    except Exception as e:
        send_telegram(f"❗️ Помилка моніторингу: {e}")


if __name__ == "__main__":
    main()
