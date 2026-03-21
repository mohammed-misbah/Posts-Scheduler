from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from zoneinfo import ZoneInfo

from app.database.db import SessionLocal
from app.models.post import Post
from app.tasks import send_post_task

scheduler = BackgroundScheduler()
IST = ZoneInfo("Asia/Kolkata")


def send_scheduled_posts():
    print("Scheduler running:", datetime.now(IST))

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
                # ✅ ONLY THIS LINE MATTERS
                send_post_task.delay(post.id)

                # mark as queued (not sent)
                post.status = "queued"

            except Exception as e:
                print(f"Queue failed for post {post.id}:", e)
                post.status = "failed"

        db.commit()

    except Exception as e:
        print("Scheduler error:", e)
        db.rollback()

    finally:
        db.close()


def start_scheduler():
    if not scheduler.running:
        scheduler.add_job(
            send_scheduled_posts,
            "interval",
            seconds=30,
            id="post_scheduler",
            replace_existing=True
        )
        scheduler.start()


def stop_scheduler():
    if scheduler.running:
        scheduler.shutdown()