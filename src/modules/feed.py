import feedparser
import time
from datetime import datetime
from modules.episode import Episode


class Feed:
    def __init__(self, feed_name: str, feed_url: str):
        print(f"Initializing {feed_name} feed with URL: {feed_url}")
        self.name = feed_name
        self.url = feed_url

    def get_latest_episode(self):
        # Parse the feed and handle any potential errors
        try:
            print(f"Parsing {self.name} feed: {self.url}")
            feed_response = feedparser.parse(self.url)
            if feed_response.bozo:
                print(f"Error parsing feed: {feed_response.bozo_exception}")
            else:
                if not feed_response.entries:
                    raise ValueError(f"No entries found in the {feed_name} feed.")
                latest_episode_json = feed_response.entries[0]
                print(
                    f"Feed parsed successfully with {len(feed_response.entries)} entries."
                )
        except Exception as e:
            print(f"Error during feed parsing: {e}")
            raise
        print(f"Fetching latest episode of {self.name}")
        latest_episode_title = latest_episode_json.title
        latest_episode_datetime = datetime.fromtimestamp(
            time.mktime(latest_episode_json.published_parsed)
        )
        latest_episode_url = latest_episode_json.enclosures[0].href

        latest_episode = Episode(
            self.name,
            latest_episode_title,
            latest_episode_url,
            latest_episode_datetime,
        )

        return latest_episode
