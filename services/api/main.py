from fastapi import FastAPI
from .routers import articles, rss_feeds
from shared.db.session import engine
from shared.db.models import Base

app = FastAPI(title="ArticleFlow API")

app.include_router(articles.router)
app.include_router(rss_feeds.router)


Base.metadata.create_all(bind=engine)

@app.get("/")
def read_root():
    return {"message": "Welcome to ArticleFlow API"}