from typing import Optional
from sqlalchemy.orm import Session
from .session import SessionLocal
from .models import RssFeed


class RssFeedRepository:
    def __init__(self, db: Optional[Session] = None):
        self.db = db or SessionLocal()

    def list_paginated(self, page: int = 1, per_page: int = 10, active_only: bool = False):
        offset = (page - 1) * per_page
        query = self.db.query(RssFeed)
        if active_only:
            query = query.filter(RssFeed.is_active == True)
        query = query.offset(offset).limit(per_page)
        return query.all()

    def find_by_id(self, feed_id: int) -> Optional[RssFeed]:
        return self.db.query(RssFeed).filter(RssFeed.id == feed_id).first()

    def find_by_url(self, url: str) -> Optional[RssFeed]:
        return self.db.query(RssFeed).filter(RssFeed.url == url).first()

    def insert(self, feed_data: dict):
        feed = RssFeed(**feed_data)
        self.db.add(feed)
        self.db.commit()
        self.db.refresh(feed)
        return feed

    def update(self, feed_id: int, feed_data: dict):
        feed = self.find_by_id(feed_id)
        if feed:
            for key, value in feed_data.items():
                setattr(feed, key, value)
            self.db.commit()
            self.db.refresh(feed)
        return feed

    def delete(self, feed_id: int):
        feed = self.find_by_id(feed_id)
        if feed:
            self.db.delete(feed)
            self.db.commit()
            return True
        return False