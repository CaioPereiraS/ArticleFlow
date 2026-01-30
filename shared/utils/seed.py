import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import csv
from shared.db.rss_feed_repository import RssFeedRepository


def seed_feeds():
    repo = RssFeedRepository()
    csv_path = os.path.join(os.path.dirname(__file__), 'feeds.csv')
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            feed_data = {
                'url': row['url'],
                'name': row['name'],
                'use_headers': False,
                'is_active': True
            }
            repo.insert(feed_data)
    print("Feeds seeded successfully.")


if __name__ == "__main__":
    seed_feeds()