import feedparser
from modules.episode import Episode
from datetime import date


class Feed:
    def __init__(self, feed_url: str):
        print(f"Initializing Feed with URL: {feed_url}")
        self.feed_url = feed_url

        # Parse the feed and handle any potential errors
        try:
            print(f"Parsing feed: {feed_url}")
            self.feed_response = feedparser.parse(feed_url)
            if self.feed_response.bozo:
                print(f"Error parsing feed: {self.feed_response.bozo_exception}")
            else:
                print(
                    f"Feed parsed successfully with {len(self.feed_response.entries)} entries."
                )
        except Exception as e:
            print(f"Error during feed parsing: {e}")
            raise

    def get_interview_episodes(self, episode_limit=0):
        print(f"Fetching interview episodes. Limit: {episode_limit}")
        episodes_dict = {}

        # Filter episode elements based on the title condition
        episode_elements = [
            episode_element
            for episode_element in self.feed_response.entries[:]
            if episode_element.title[-29:] == " Interview with Throwing Fits"
        ]

        print(f"Found {len(episode_elements)} interview episodes.")

        # Limit the number of episodes to the specified limit, if any
        if episode_limit > 0:
            print(f"Applying episode limit: {episode_limit}")
            episode_elements = episode_elements[-1 * episode_limit :]

        # Extract episode details and create Episode objects
        for episode_element in episode_elements:
            print(f"Processing episode: {episode_element.title}")
            try:
                episode = Episode(
                    title=episode_element.title,
                    url=episode_element.enclosures[0].href,
                    release_date=date(
                        episode_element.published_parsed.tm_year,
                        episode_element.published_parsed.tm_mon,
                        episode_element.published_parsed.tm_mday,
                    ),
                )
                episodes_dict[episode_element.title] = episode
                print(f"Added episode: {episode.title} to the dictionary.")
            except Exception as e:
                print(f"Error processing episode {episode_element.title}: {e}")

        print(f"Returning {len(episodes_dict)} episodes.")
        return episodes_dict
