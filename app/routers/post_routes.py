import os
import shutil
from app.models.post import Post
from fastapi import APIRouter, Depends, UploadFile, File, Form
from sqlalchemy.orm import Session
from datetime import datetime
from app.database.db import SessionLocal
from app.services.post_service import create_post, get_all_posts, delete_post

router = APIRouter()

MEDIA_FOLDER = "media"


def get_db():

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/")
def create_new_post(
    content: str = Form(...),
    scheduled_time: datetime = Form(...),
    media: UploadFile = File(None),
    db: Session = Depends(get_db)
):

    media_path = None

    if media:

        os.makedirs(MEDIA_FOLDER, exist_ok=True)

        file_path = os.path.join(MEDIA_FOLDER, media.filename)

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(media.file, buffer)

        media_path = file_path

    post = create_post(db, content, scheduled_time, media_path)

    return {
        "message": "Post created successfully",
        "post_id": post.id
    }


@router.put("/{post_id}")
def reschedule_post(post_id: int, scheduled_time: datetime, db: Session = Depends(get_db)):

    post = db.query(Post).filter(Post.id == post_id).first()

    if not post:
        return {"error": "Post not found"}

    post.scheduled_time = scheduled_time
    db.commit()

    return {"message": "Post rescheduled successfully"}


@router.put("/edit_post/{post_id}")
def edit_post(
    post_id: int,
    content: str = Form(...),
    media: UploadFile = File(None),
    db: Session = Depends(get_db)
):
    post = db.query(Post).filter(Post.id == post_id).first()

    if not post:
        return {"error": "Post not found"}

    post.content = content

    if media:
        os.makedirs(MEDIA_FOLDER, exist_ok=True)

        file_path = os.path.join(MEDIA_FOLDER, media.filename)

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(media.file, buffer)

        post.media_type = "image"   # adjust if needed
        # update media table here if you use it

    db.commit()

    return {"message": "Post updated successfully"}


# List All Post
@router.get("/posts")
def list_posts(db: Session = Depends(get_db)):

    posts = get_all_posts(db)

    return posts


# List Scheduled Post
@router.get("/posts/scheduled")
def scheduled_posts(db: Session = Depends(get_db)):
    return db.query(Post).filter(
        Post.status == "pending",
        Post.scheduled_time > datetime.now()
    ).all()


# List Published Post
@router.get("/posts/published")
def published_posts(db: Session = Depends(get_db)):
    return db.query(Post).filter(Post.status == "sent").all()


@router.delete("/delete-post/{post_id}")
def remove_post(post_id: int, db: Session = Depends(get_db)):

    delete_post(db, post_id)

    return {"message": "Post deleted successfully"}