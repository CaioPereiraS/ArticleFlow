import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from newspaper import Article as NewspaperArticle
from shared.db.article_repository import ArticleRepository
from dateutil import parser as date_parser

class ArticleGateway:
    def process_article(self, article_data: dict) -> bool:
        try:
            url = article_data.get('url')
            feed_id = article_data.get('feed_id')
            feed_name = article_data.get('feed_name')
            title_from_feed = article_data.get('title')
            published_from_feed = article_data.get('published')

            if not url or not feed_id:
                print("Missing url or feed_id in article_data")
                return False

            # Extract article using newspaper4k
            article = NewspaperArticle(url)
            article.download()
            article.parse()
            article.nlp()  # For summary

            # Prepare data for saving
            data = {
                'title': article.title or title_from_feed or 'Unknown Title',
                'url': url,
                'content': article.text or '',
                'summary': article.summary or '',
                'source': feed_name or article.source_url or '',
                'feed_id': feed_id
            }

            # Use publish date from newspaper if available, else from feed
            if article.publish_date:
                data['published_at'] = article.publish_date
            elif published_from_feed:
                try:
                    data['published_at'] = date_parser.parse(published_from_feed)
                except:
                    pass

            # Save to database
            repo = ArticleRepository()
            repo.insert(data)
            repo.db.close()  # Close session

            print(f"Article saved: {data['title']}")
            return True

        except Exception as e:
            print(f"Error processing article {article_data.get('url')}: {e}")
            return False
        
    def test_article_url(self, url: str) -> bool:
        try:
            article = NewspaperArticle(url)
            article.download()
            article.parse()
            print(f"Article Title: {article.title}")
            print(f"Article Text: {article.text[:200]}...")  # Print first 200 chars
            return True
        except Exception as e:
            print(f"Error testing article URL {url}: {e}")
            return False

if __name__ == "__main__":
    gateway = ArticleGateway()
    test_url = "https://www.npr.org/2026/01/08/g-s1-105040/up-first-newsletter-ice-shooting-minneapolis-venezuela-tanker-dietary-guidelines"
    gateway.test_article_url(test_url)