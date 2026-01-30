import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..schemas import ArticleCreate, ArticleUpdate, ArticleResponse
from shared.db.session import SessionLocal
from shared.db.article_repository import ArticleRepository
from shared.db.rss_feed_repository import RssFeedRepository

router = APIRouter(prefix="/articles", tags=["articles"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/", response_model=List[ArticleResponse])
def list_articles(page: int = 1, per_page: int = 10, db: Session = Depends(get_db)):
    repo = ArticleRepository(db)
    articles = repo.list_paginated(page, per_page)
    return articles


@router.get("/{article_id}", response_model=ArticleResponse)
def get_article(article_id: int, db: Session = Depends(get_db)):
    repo = ArticleRepository(db)
    article = repo.find_by_id(article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    return article


@router.post("/", response_model=ArticleResponse)
def create_article(article: ArticleCreate, db: Session = Depends(get_db)):
    repo = ArticleRepository(db)
    feed_repo = RssFeedRepository(db)
    if not feed_repo.find_by_id(article.feed_id):
        raise HTTPException(status_code=400, detail="Feed not found")
    existing = repo.find_by_url(article.url)
    if existing:
        raise HTTPException(status_code=400, detail="Article with this URL already exists")
    return repo.insert(article.dict())


@router.put("/{article_id}", response_model=ArticleResponse)
def update_article(article_id: int, article: ArticleUpdate, db: Session = Depends(get_db)):
    repo = ArticleRepository(db)
    feed_repo = RssFeedRepository(db)
    update_data = article.dict(exclude_unset=True)
    if 'feed_id' in update_data:
        if not feed_repo.find_by_id(update_data['feed_id']):
            raise HTTPException(status_code=400, detail="Feed not found")
    if 'url' in update_data:
        existing = repo.find_by_url(update_data['url'])
        if existing and existing.id != article_id: # type: ignore[operator]
            raise HTTPException(status_code=400, detail="Another Article with this URL already exists")
    updated = repo.update(article_id, update_data)
    if not updated:
        raise HTTPException(status_code=404, detail="Article not found")
    return updated


@router.delete("/{article_id}")
def delete_article(article_id: int, db: Session = Depends(get_db)):
    repo = ArticleRepository(db)
    if not repo.delete(article_id):
        raise HTTPException(status_code=404, detail="Article not found")
    return {"message": "Article deleted"}