import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..schemas import RssFeedCreate, RssFeedUpdate, RssFeedResponse
from shared.db.session import SessionLocal
from shared.db.rss_feed_repository import RssFeedRepository

router = APIRouter(prefix="/rss-feeds", tags=["rss-feeds"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/", response_model=List[RssFeedResponse])
def list_rss_feeds(page: int = 1, per_page: int = 10, db: Session = Depends(get_db)):
    repo = RssFeedRepository(db)
    feeds = repo.list_paginated(page, per_page)
    return feeds


@router.get("/{feed_id}", response_model=RssFeedResponse)
def get_rss_feed(feed_id: int, db: Session = Depends(get_db)):
    repo = RssFeedRepository(db)
    feed = repo.find_by_id(feed_id)
    if not feed:
        raise HTTPException(status_code=404, detail="RSS Feed not found")
    return feed


@router.post("/", response_model=RssFeedResponse)
def create_rss_feed(feed: RssFeedCreate, db: Session = Depends(get_db)):
    repo = RssFeedRepository(db)
    existing = repo.find_by_url(feed.url)
    if existing is not None:
        raise HTTPException(status_code=400, detail="RSS Feed with this URL already exists")
    return repo.insert(feed.dict())


@router.put("/{feed_id}", response_model=RssFeedResponse)
def update_rss_feed(feed_id: int, feed: RssFeedUpdate, db: Session = Depends(get_db)):
    repo = RssFeedRepository(db)
    update_data = feed.dict(exclude_unset=True)
    if 'url' in update_data:
        existing = repo.find_by_url(update_data['url'])
        if existing is not None and existing.id != feed_id: # type: ignore[operator]
            raise HTTPException(status_code=400, detail="Another RSS Feed with this URL already exists")
    updated = repo.update(feed_id, update_data)
    if not updated:
        raise HTTPException(status_code=404, detail="RSS Feed not found")
    return updated


@router.delete("/{feed_id}")
def delete_rss_feed(feed_id: int, db: Session = Depends(get_db)):
    repo = RssFeedRepository(db)
    if not repo.delete(feed_id):
        raise HTTPException(status_code=404, detail="RSS Feed not found")
    return {"message": "RSS Feed deleted"}