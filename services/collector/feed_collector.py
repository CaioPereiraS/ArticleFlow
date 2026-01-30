import sys
import os
from time import time
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


import feedparser
from shared.db.rss_feed_repository import RssFeedRepository
from shared.rabbitmq_manager import RabbitMQManager

INTERVAL_SECONDS = 300  # 5 minutos

class FeedCollector:
   def __init__(self):
      self.rabbitmq = RabbitMQManager()
      self.rabbitmq.setup()
   
   def run(self):
      while True:
         try:
            feed_repo = RssFeedRepository()
            feeds = feed_repo.list_paginated(page=1, per_page=10,active_only=True)
            for feed in feeds:
                self.process_feed(feed)
         except Exception as e:
             print(f"Error in feed collection: {e}")
         finally:
            feed_repo.db.close()
         #time.sleep(INTERVAL_SECONDS)

   def process_feed(self, feed):
        parsed_feed = feedparser.parse(feed.url)

        for entry in parsed_feed.entries:
            payload = {
                "feed_id": feed.id,
                "feed_name": feed.name,
                "title": entry.title,
                "url": entry.link,
                "published": getattr(entry, "published", None)
            }

            self.rabbitmq.publish(payload)

if __name__ == "__main__":
      collector = FeedCollector()
      collector.run()