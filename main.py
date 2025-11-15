import time
import hmac
import hashlib
import base64
import json
import os
import requests


APP_KEY = os.environ["APP_KEY"]
APP_SECRET = os.environ["APP_SECRET"]
DEVICE_SN = os.environ["DEVICE_SN"]
TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]


def sign(timestamp):
    message = APP_KEY + str(timestamp)
    sign = hmac.new(
        APP_SECRET.encode("utf-8"),
        msg=message.encode("utf-8"),
        digestmod=hashlib.sha256,
    ).digest()
    return base64.b64encode(sign).decode()


def get_ecoflow_status():
    url = "https://api.ecoflow.com/iot-open/sign/device/queryDeviceQuota"
    ts = int(time.time() * 1000)

    headers = {
        "appKey": APP_KEY,
        "timestamp": str(ts),
        "sign": sign(ts),
        "Content-Type": "application/json",
    }

    data = {"sn": DEVICE_SN}

    response = requests.post(url, headers=headers, data=json.dumps(data))
    response.raise_for_status()
    return response.json()


def send_telegram(message: str):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": TELEGRAM_CHAT_ID, "text": message})


def main_loop():
    last_state = None

    while True:
        try:
            data = get_ecoflow_status()

            soc = data["data"]["soc"]
            watts_out = data["data"]["wattsOut"]
            watts_in = data["data"]["wattsIn"]

            # визначення стану
            if watts_in > 50:
                state = "charging"
            elif watts_out > 50:
                state = "discharging"
            else:
                state = "idle"

            if state != last_state:
                send_telegram(
                    f"🔔 EcoFlow Delta 2 Max:\n"
                    f"Стан: {state}\n"
                    f"🔋 SOC: {soc}%\n"
                    f"⚡ Заряд: +{watts_in} Вт | Розряд: -{watts_out} Вт"
                )
                last_state = state

        except Exception as e:
            send_telegram(f"❗️ Помилка моніторингу: {e}")

        time.sleep(60)


if __name__ == "__main__":
    main_loop()
