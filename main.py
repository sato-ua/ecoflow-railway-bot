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
    digest = hmac.new(
        APP_SECRET.encode("utf-8"),
        msg=message.encode("utf-8"),
        digestmod=hashlib.sha256
    ).digest()
    return base64.b64encode(digest).decode()

def get_ecoflow_status():
    # спробуй з api-e.ecoflow.com, якщо основний не працює
    url = "https://api.ecoflow.com/iot-open/sign/device/quota/all"
    print("DEBUG: запит URL =", url)
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
    print("DEBUG: статус:", response.status_code, "відповідь:", response.text)
    response.raise_for_status()
    return response.json()

def send_telegram(text: str):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    requests.post(url, json={
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text
    })

def main_loop():
    last_state = None
    while True:
        try:
            data = get_ecoflow_status()
            quota = data["data"]["quota"]
            soc = quota.get("soc")
            watts_in = quota.get("wattsInSum", 0)
            watts_out = quota.get("wattsOutSum", 0)

            if watts_in > 30:
                state = "charging"
            elif watts_out > 30:
                state = "discharging"
            else:
                state = "idle"

            if state != last_state:
                send_telegram(
                    f"🔔 EcoFlow Delta 2 Max:\n"
                    f"Стан: {state}\n"
                    f"🔋 SOC: {soc}%\n"
                    f"⚡ Вхід: +{watts_in} Вт\n"
                    f"⚡ Вихід: -{watts_out} Вт"
                )
                last_state = state

        except Exception as e:
            send_telegram(f"❗️ Помилка моніторингу: {e}")

        time.sleep(60)

if __name__ == "__main__":
    main_loop()
