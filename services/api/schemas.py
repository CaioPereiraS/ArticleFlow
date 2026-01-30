from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class RssFeedBase(BaseModel):
    url: str
    name: str
    is_active: Optional[bool] = True
    use_headers: Optional[bool] = False
    headers: Optional[str] = None


class RssFeedCreate(RssFeedBase):
    pass


class RssFeedUpdate(BaseModel):
    id: int
    url: Optional[str] = None
    name: Optional[str] = None
    is_active: Optional[bool] = None
    use_headers: Optional[bool] = None
    headers: Optional[str] = None


class RssFeedResponse(RssFeedBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class ArticleBase(BaseModel):
    title: str
    url: str
    content: str
    summary: Optional[str] = None
    source: Optional[str] = None
    published_at: Optional[datetime] = None
    feed_id: int


class ArticleCreate(ArticleBase):
    pass


class ArticleUpdate(BaseModel):
    title: Optional[str] = None
    url: Optional[str] = None
    content: Optional[str] = None
    summary: Optional[str] = None
    source: Optional[str] = None
    published_at: Optional[datetime] = None
    feed_id: Optional[int] = None


class ArticleResponse(ArticleBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    feed: RssFeedResponse

    class Config:
        from_attributes = True