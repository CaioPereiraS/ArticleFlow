from sqlalchemy.orm import Session, joinedload
from typing import Optional
from .session import SessionLocal
from .models import Article


class ArticleRepository:
    def __init__(self, db: Optional[Session] = None):
        self.db = db or SessionLocal()

    def list_paginated(self, page: int = 1, per_page: int = 10):
        offset = (page - 1) * per_page
        return self.db.query(Article).options(joinedload(Article.feed)).offset(offset).limit(per_page).all()

    def find_by_id(self, article_id: int) -> Optional[Article]:
        return self.db.query(Article).options(joinedload(Article.feed)).filter(Article.id == article_id).first()

    def find_by_url(self, url: str) -> Optional[Article]:
        return self.db.query(Article).options(joinedload(Article.feed)).filter(Article.url == url).first()

    def insert(self, article_data: dict):
        article = Article(**article_data)
        self.db.add(article)
        self.db.commit()
        self.db.refresh(article)
        return article

    def update(self, article_id: int, article_data: dict):
        article = self.find_by_id(article_id)
        if article:
            for key, value in article_data.items():
                setattr(article, key, value)
            self.db.commit()
            self.db.refresh(article)
        return article

    def delete(self, article_id: int):
        article = self.find_by_id(article_id)
        if article:
            self.db.delete(article)
            self.db.commit()
            return True
        return False