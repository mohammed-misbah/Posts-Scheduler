from apscheduler.schedulers.background import BackgroundScheduler
import os
import time
from app.database.db import SessionLocal
from app.models.post import Post
from app.models.media import Media
from app.telegram_bot import (
    send_carousel_as_pdf,
    send_long_message,
    send_photo,
    send_video,
    send_document
)
from datetime import datetime
from zoneinfo import ZoneInfo

scheduler = BackgroundScheduler()

IST = ZoneInfo("Asia/Kolkata")
BASE_DIR = os.getcwd()

def send_scheduled_posts():

    print("Scheduler running:", datetime.now(ZoneInfo("Asia/Kolkata")))

    db = SessionLocal()

    try:

        posts = (
            db.query(Post)
            .filter(
                Post.status == "pending",
                Post.scheduled_time <= datetime.now(IST)
            )
            .order_by(Post.scheduled_time)
            .all()
        )

        for post in posts:
            try:
                media_files = (
                    db.query(Media)
                    .filter(Media.post_id == post.id)
                    .order_by(Media.order_index)
                    .all()
                )

                if post.media_type == "none":
                    # send_text_message(post.content)
                    send_long_message(post.content)
                    post.status = "sent"

                elif post.media_type == "image" and media_files:

                    file_path = os.path.join(BASE_DIR, media_files[0].file_path)


                    try:
                        send_photo(file_path, post.content)
                        post.status = "sent"
                    finally:
                        if os.path.exists(file_path):
                            os.remove(file_path)
                        db.delete(media_files[0])
                        db.flush()

                elif post.media_type == "video" and media_files:

                    file_path = os.path.join(BASE_DIR, media_files[0].file_path)


                    try:
                        send_video(file_path, post.content)
                        post.status = "sent"
                    finally:
                        if os.path.exists(file_path):
                            os.remove(file_path)
                        db.delete(media_files[0])
                        db.flush()

                elif post.media_type == "pdf" and media_files:

                    file_path = os.path.join(BASE_DIR, media_files[0].file_path)


                    try:
                        send_document(file_path, post.content)
                        post.status = "sent"
                    finally:
                        if os.path.exists(file_path):
                            os.remove(file_path)
                        db.delete(media_files[0])
                        db.flush()

                elif post.media_type == "carousel" and media_files:

                    images = [os.path.join(BASE_DIR, m.file_path) for m in media_files]

                    try:
                        formatted_text = f"{post.content}\n\n📄 Swipe the document below 👇"

                        send_long_message(formatted_text)

                        time.sleep(0.8)

                        res = send_carousel_as_pdf(images, "")

                        if not res or not res.get("ok"):
                            raise Exception("Telegram failed")
                        
                        post.status = "sent"

                    finally:
                        for path in images:
                            print("DELETE PATH:", path)
                            print("EXISTS:", os.path.exists(path))
                            if os.path.exists(path):
                                os.remove(path)

                        for m in media_files:
                            db.delete(m)
                        db.flush()
                
            except Exception as e:
                print(f"Failed post {post.id}:", e)
                post.status = "failed"
                continue

        db.commit()

    except Exception as e:
        print("Scheduler error:", e)
        db.rollback()

    finally:
        db.close()


def start_scheduler():
    if not scheduler.running:
        scheduler.add_job(send_scheduled_posts, "interval", seconds=30, id="post_scheduler", replace_existing=True )
        # scheduler.add_job(send_scheduled_posts, "cron", hour=8, minute=58 )
        scheduler.start()


def stop_scheduler():
    if scheduler.running:
        scheduler.shutdown()