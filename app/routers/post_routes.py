import os
import uuid
import shutil
import json
from typing import List

from fastapi import APIRouter, Depends, UploadFile, File, Form
from sqlalchemy.orm import Session
from datetime import datetime

from app.database.db import SessionLocal
from app.models.post import Post
from app.models.media import Media
from app.services.post_service import create_post, get_all_posts, delete_post

router = APIRouter()

MEDIA_FOLDER = "media"
os.makedirs(MEDIA_FOLDER, exist_ok=True)

# ---------------- DB ---------------- #
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------------- CREATE POST ---------------- #
@router.post("/")
def create_new_post(
    content: str = Form(...),
    scheduled_time: datetime = Form(...),
    media: List[UploadFile] = File(None),
    media_paths: str = Form(None),
    db: Session = Depends(get_db)
):

    post = create_post(db, content, scheduled_time)

    # ==============================
    # ✅ CASE 1: CAROUSEL (USE PATHS)
    # ==============================
    if media_paths:
        paths = json.loads(media_paths)

        for index, path in enumerate(paths):
            db.add(Media(
                post_id=post.id,
                file_path=path,
                order_index=index
            ))

        post.media_type = "carousel"

    # ==============================
    # ✅ CASE 2: NORMAL FILE UPLOAD
    # ==============================
    elif media:
        for index, file in enumerate(media):

            ext = file.filename.split(".")[-1]
            filename = f"{uuid.uuid4()}.{ext}"
            file_path = os.path.join(MEDIA_FOLDER, filename)

            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

            db.add(Media(
                post_id=post.id,
                file_path=file_path,
                order_index=index
            ))

        if len(media) > 1:
            post.media_type = "carousel"
        else:
            content_type = media[0].content_type

            if content_type.startswith("image"):
                post.media_type = "image"
            elif content_type.startswith("video"):
                post.media_type = "video"
            else:
                post.media_type = "pdf"

    # ==============================
    db.commit()

    return {"message": "Post created successfully", "post_id": post.id}


# ---------------- UPLOAD FROM CAROUSEL BUILDER ---------------- #
@router.post("/upload-carousel")
async def upload_carousel(files: list[UploadFile] = File(...)):

    uploaded_files = []

    for file in files:
        ext = file.filename.split(".")[-1]
        filename = f"{uuid.uuid4()}.{ext}"
        filepath = os.path.join(MEDIA_FOLDER, filename)

        with open(filepath, "wb") as f:
            f.write(await file.read())

        uploaded_files.append(filepath)

    return {"paths": uploaded_files}


# ---------------- RESCHEDULE ---------------- #
@router.put("/{post_id}")
def reschedule_post(post_id: int, scheduled_time: datetime, db: Session = Depends(get_db)):

    post = db.query(Post).filter(Post.id == post_id).first()

    if not post:
        return {"error": "Post not found"}

    post.scheduled_time = scheduled_time
    db.commit()

    return {"message": "Post rescheduled successfully"}


# ---------------- EDIT POST ---------------- #
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
        file_path = os.path.join(MEDIA_FOLDER, media.filename)

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(media.file, buffer)

        post.media_type = "image"

    db.commit()

    return {"message": "Post updated successfully"}


# ---------------- LIST POSTS ---------------- #
@router.get("/posts")
def list_posts(db: Session = Depends(get_db)):
    return get_all_posts(db)


@router.get("/posts/scheduled")
def scheduled_posts(db: Session = Depends(get_db)):
    return db.query(Post).filter(
        Post.status == "pending",
        Post.scheduled_time > datetime.now()
    ).all()


@router.get("/posts/published")
def published_posts(db: Session = Depends(get_db)):
    return db.query(Post).filter(Post.status == "sent").all()


# ---------------- DELETE POST ---------------- #
@router.delete("/delete-post/{post_id}")
def remove_post(post_id: int, db: Session = Depends(get_db)):
    delete_post(db, post_id)
    return {"message": "Post deleted successfully"}