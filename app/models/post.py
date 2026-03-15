from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime
from app.database.db import Base
from sqlalchemy.orm import relationship


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    media_type = Column(String, default="none")  # none | image | video | pdf | carousel
    scheduled_time = Column(DateTime(timezone=True), nullable=False)
    status = Column(String, default="pending")  # pending | sent

    media = relationship("Media", cascade="all, delete")