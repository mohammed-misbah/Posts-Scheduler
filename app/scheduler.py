from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy.orm import Session
from datetime import datetime

from app.database.db import SessionLocal
from app.models.post import Post
from app.models.media import Media
from app.telegram_bot import (
    send_text_message,
    send_photo,
    send_video,
    send_document
)
from datetime import datetime
from zoneinfo import ZoneInfo

scheduler = BackgroundScheduler()


def send_scheduled_posts():

    db = SessionLocal()

    try:

        posts = (
            db.query(Post)
            .filter(
                Post.status == "pending",
                Post.scheduled_time <= datetime.now(ZoneInfo("Asia/Kolkata"))
            )
            .order_by(Post.scheduled_time)
            .all()
        )

        for post in posts:

            media_files = (
                db.query(Media)
                .filter(Media.post_id == post.id)
                .order_by(Media.order_index)
                .all()
            )

            if post.media_type == "none":
                send_text_message(post.content)

            elif post.media_type == "image" and media_files:
                send_photo(media_files[0].file_path, post.content)

            elif post.media_type == "video" and media_files:
                send_video(media_files[0].file_path, post.content)

            elif post.media_type == "pdf" and media_files:
                send_document(media_files[0].file_path, post.content)

            elif post.media_type == "carousel":
                first = True
                for media in media_files:
                    if first:
                        send_photo(media.file_path, post.content)
                        first = False
                    else:
                        send_photo(media.file_path, "")

            post.status = "sent"

        db.commit()

    except Exception as e:
        print("Scheduler error:", e)
        db.rollback()

    finally:
        db.close()


def start_scheduler():

    scheduler.add_job(send_scheduled_posts, "interval", seconds=30)

    # scheduler.add_job(send_scheduled_posts, "cron", hour=8, minute=58 )

    scheduler.start()