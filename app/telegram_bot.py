import requests
from app.config import settings

BASE_URL = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}"


def send_text_message(text):

    url = f"{BASE_URL}/sendMessage"

    payload = {
        "chat_id": settings.TELEGRAM_CHAT_ID,
        "text": text
    }

    response = requests.post(url, json=payload, timeout=20)

    if response.status_code != 200:
        print("Telegram error:", response.text)


def send_photo(photo_path, caption):

    url = f"{BASE_URL}/sendPhoto"

    with open(photo_path, "rb") as photo:

        files = {"photo": photo}

        data = {
            "chat_id": settings.TELEGRAM_CHAT_ID,
            "caption": caption
        }

        response = requests.post(url, data=data, files=files, timeout=20)

        if response.status_code != 200:
            print("Telegram error:", response.text)


def send_video(video_path, caption):

    url = f"{BASE_URL}/sendVideo"

    with open(video_path, "rb") as video:

        files = {"video": video}

        data = {
            "chat_id": settings.TELEGRAM_CHAT_ID,
            "caption": caption
        }

        response = requests.post(url, data=data, files=files, timeout=20)

        if response.status_code != 200:
            print("Telegram error:", response.text)


def send_document(file_path, caption):

    url = f"{BASE_URL}/sendDocument"

    with open(file_path, "rb") as file:

        files = {"document": file}

        data = {
            "chat_id": settings.TELEGRAM_CHAT_ID,
            "caption": caption
        }

        response = requests.post(url, data=data, files=files, timeout=20)

        if response.status_code != 200:
            print("Telegram error:", response.text)