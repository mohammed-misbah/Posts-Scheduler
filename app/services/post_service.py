from sqlalchemy.orm import Session
from datetime import datetime

from app.models.post import Post
from app.models.media import Media


from sqlalchemy.orm import Session
from app.models.post import Post
from app.models.media import Media
import os


def create_post(db: Session, content: str, scheduled_time, media_path: str = None):

    new_post = Post(
        content=content,
        scheduled_time=scheduled_time,
        media_type="none" if not media_path else "image",
        status="pending"
    )

    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    if media_path:
        media = Media(
            post_id=new_post.id,
            file_path=media_path,
            order_index=0
        )
        db.add(media)
        db.commit()

    return new_post


def get_all_posts(db: Session):
    return db.query(Post).all()


def get_pending_posts(db: Session):
    return db.query(Post).filter(Post.status == "pending").all()


def get_post_by_id(db: Session, post_id: int):
    return db.query(Post).filter(Post.id == post_id).first()



def delete_post(db: Session, post_id: int):
    post = db.query(Post).filter(Post.id == post_id).first()

    if not post:
        return None

    # Delete all media files (image, video, pdf, carousel)
    for media in post.media:
        try:
            if media.file_path and os.path.exists(media.file_path):
                os.remove(media.file_path)
        except Exception as e:
            print(f"File delete error: {media.file_path} -> {e}")

    # Delete post (media rows auto deleted via cascade)
    db.delete(post)
    db.commit()

    return True