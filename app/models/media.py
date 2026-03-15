from sqlalchemy import Column, Integer, String, ForeignKey
from app.database.db import Base


class Media(Base):
    __tablename__ = "media"

    id = Column(Integer, primary_key=True, index=True)

    post_id = Column(Integer, ForeignKey("posts.id", ondelete="CASCADE"))

    file_path = Column(String, nullable=False)

    order_index = Column(Integer, default=0)