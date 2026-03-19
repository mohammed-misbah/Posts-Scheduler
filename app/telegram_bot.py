import os
import json
import uuid
import requests
from PIL import Image
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
        

def send_long_message(text):
    max_len = 4000

    while text:
        chunk = text[:max_len]

        # try to cut at last newline
        if len(text) > max_len:
            last_newline = chunk.rfind("\n")
            if last_newline != -1:
                chunk = chunk[:last_newline]

        send_text_message(chunk.strip())
        text = text[len(chunk):]


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




def send_carousel_as_pdf(images, caption):
    pdf_path = f"carousel_{uuid.uuid4()}.pdf"
    thumb_path = f"thumb_{uuid.uuid4()}.jpg"

    try:
        url = f"{BASE_URL}/sendDocument"

        pil_images = []

        for img_path in images:
            img = Image.open(img_path).convert("RGB")
            pil_images.append(img)

        pil_images[0].save(
            pdf_path,
            save_all=True,
            append_images=pil_images[1:]
        )

        thumb_img = Image.open(images[0]).convert("RGB")
        thumb_img.thumbnail((320, 320))
        thumb_img.save(thumb_path, "JPEG", quality=70)

        with open(pdf_path, "rb") as file, open(thumb_path, "rb") as thumb:

            files = {
                "document": file,
                "thumb": thumb
            }

            data = {
                "chat_id": settings.TELEGRAM_CHAT_ID,
                "caption": caption
            }

            response = requests.post(url, data=data, files=files)

            print("PDF RESPONSE:", response.text)

        return response.json()

    except Exception as error:
        raise RuntimeError(f"Failed to send PDF: {error}")

    finally:
        if os.path.exists(pdf_path):
            os.remove(pdf_path)
        if os.path.exists(thumb_path):
            os.remove(thumb_path)