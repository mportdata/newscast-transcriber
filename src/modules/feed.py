import feedparser
from modules.episode import Episode
from datetime import date


class Feed:
    def __init__(self, feed_url: str):
        self.feed_url = feed_url
        self.feed_response = feedparser.parse(feed_url)

    def get_interview_episodes(self, episode_limit=0):
        episodes_dict = {}
        episode_elements = [
            episode_element
            for episode_element in self.feed_response.entries[:]
            if episode_element.title[-29:] == " Interview with Throwing Fits"
        ]
        for episode_element in episode_elements[-1 * episode_limit :]:
            episodes_dict[episode_element.title] = Episode(
                title=episode_element.title,
                url=episode_element.enclosures[0].href,
                release_date=date(
                    episode_element.published_parsed.tm_year,
                    episode_element.published_parsed.tm_mon,
                    episode_element.published_parsed.tm_mday,
                ),
            )

        return episodes_dict
