from app.celery import celery
from app.database.db import SessionLocal
from app.models.post import Post
from app.models.media import Media
from celery.exceptions import MaxRetriesExceededError

import os
import time

from app.telegram_bot import (
    send_carousel_as_pdf,
    send_long_message,
    send_photo,
    send_video,
    send_document
)


@celery.task(bind=True, max_retries=3, default_retry_delay=10)
def send_post_task(self, post_id: int):

    db = SessionLocal()

    try:
        post = db.query(Post).filter(Post.id == post_id).first()

        # prevent duplicate execution
        if not post or post.status not in ["pending", "queued"]:
            return

        # lock the post
        post.status = "processing"
        db.commit()

        media_files = (
            db.query(Media)
            .filter(Media.post_id == post.id)
            .order_by(Media.order_index)
            .all()
        )

        # BASE_DIR = os.getcwd()
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        for img in images:
            print("Checking image path:", img, "Exists:", os.path.exists(img))

        if post.media_type == "none":
            send_long_message(post.content)

        elif post.media_type == "image" and media_files:
            path = os.path.join(BASE_DIR, media_files[0].file_path)
            send_photo(path, post.content)

        elif post.media_type == "video" and media_files:
            path = os.path.join(BASE_DIR, media_files[0].file_path)
            send_video(path, post.content)

        elif post.media_type == "pdf" and media_files:
            path = os.path.join(BASE_DIR, media_files[0].file_path)
            send_document(path, post.content)

        elif post.media_type == "carousel" and media_files:
            images = [os.path.join(BASE_DIR, m.file_path) for m in media_files]

            send_long_message(post.content)
            time.sleep(0.8)

            try:
                res = send_carousel_as_pdf(images, "")
                print("Telegram response:", res)
                if not res or not res.get("ok"):
                    raise Exception("Telegram failed")
            except Exception as e:
                print("Carousel error:", str(e))
                raise

        # success
        post.status = "sent"

        # delete media safely
        for m in media_files:
            path = os.path.join(BASE_DIR, m.file_path)

            if os.path.exists(path):
                os.remove(path)

            db.delete(m)

        db.commit()

    except MaxRetriesExceededError:
        post.status = "failed"
        db.commit()

    except Exception as e:
        db.rollback()

        post.status = "retrying"
        db.commit()

        raise self.retry(exc=e)

    finally:
        db.close()