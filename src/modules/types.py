import feedparser


class Episode:
    def __init__(self, title, url, release_date):
        self.title = title
        self.url = url
        self.release_date = release_date


class Feed:
    def __init__(self, feed_url: str):
        self.feed_url = feed_url
        self.feed_response = feedparser.parse(feed_url)
