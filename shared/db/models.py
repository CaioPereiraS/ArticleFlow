from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Boolean,
    DateTime,
    ForeignKey,
    func
)
from sqlalchemy.orm import relationship
from .base import Base


class RssFeed(Base):
    __tablename__ = "rss_feeds"

    id = Column(Integer, primary_key=True)
    url = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)

    is_active = Column(Boolean, default=True)
    use_headers = Column(Boolean, default=False)
    headers = Column(Text)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    articles = relationship("Article", back_populates="feed")


class Article(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    url = Column(String, unique=True, nullable=False)

    content = Column(Text, nullable=False)
    summary = Column(Text)
    source = Column(String)

    published_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    feed_id = Column(Integer, ForeignKey("rss_feeds.id"), nullable=False)

    feed = relationship("RssFeed", back_populates="articles")
