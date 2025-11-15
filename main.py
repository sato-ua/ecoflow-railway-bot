import time
import hmac
import hashlib
import base64
import json
import os
import requests


# ---- CONFIG (змінні з Environment Variables у Railway / Render) ----

APP_KEY = os.environ["APP_KEY"]
APP_SECRET = os.environ["APP_SECRET"]
DEVICE_SN = os.environ["DEVICE_SN"]

TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]


# ---- ПІДПИС ДЛЯ API ----

def sign(timestamp):
    message = APP_KEY + str(timestamp)
    digest = hmac.new(
        APP_SECRET.encode("utf-8"),
        msg=message.encode("utf-8"),
        digestmod=hashlib.sha256
    ).digest()

    return base64.b64encode(digest).decode()


# ---- ЗАПИТ ДО ECOFLOW API ----

def get_ecoflow_status():
    url = "https://api.ecoflow.com/iot-open/sign/device/quota/all"

    ts = int(time.time() * 1000)

    headers = {
        "appKey": APP_KEY,
        "timestamp": str(ts),
        "sign": sign(ts),
        "Content-Type": "application/json",
    }

    payload = {
        "sn": DEVICE_SN,
        "params": ["soc", "wattsInSum", "wattsOutSum"]
    }

    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()

    return response.json()


# ---- ВІДПРАВКА ПОВІДОМЛЕНЬ У TELEGRAM ----

def send_telegram(text: str):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    requests.post(url, json={
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text
    })


# ---- ОСНОВНИЙ ЦИКЛ ----

def main_loop():
    last_state = None

    while True:
        try:
            data = get_ecoflow_status()

            quota = data["data"]["quota"]

            soc = quota.get("soc")
            watts_in_
