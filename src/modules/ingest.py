import feedparser
import requests
import os
from datetime import date


def get_episode_data_from_feed(feed_url, episode_limit=0):
    episode_data = {}
    feed = feedparser.parse(feed_url)
    episodes = [
        episode
        for episode in feed.entries[:]
        if episode.title[-29:] == " Interview with Throwing Fits"
    ]
    if episode_limit > 0:
        episodes = episodes[-1 * episode_limit :]
    for episode in episodes:
        episode_title = episode.title
        episode_release_year = episode.published_parsed.tm_year
        episode_release_month = episode.published_parsed.tm_mon
        episode_release_day = episode.published_parsed.tm_mday
        episode_release_date = date(
            episode_release_year, episode_release_month, episode_release_day
        )
        episode_url = episode.enclosures[0].href
        episode_data[episode_title] = {
            "release_date": episode_release_date,
            "url": episode_url,
        }
    return episode_data


def download_episode(title, episode_url, save_dir="podcasts"):
    # Create the directory if it doesn't exist
    os.makedirs(save_dir, exist_ok=True)

    # Clean up the title for use as a filename
    safe_title = "".join([c if c.isalnum() else "_" for c in title]) + ".mp3"
    file_path = os.path.join(save_dir, safe_title)

    print(f"Downloading: {title}")

    # Download the episode using requests
    response = requests.get(episode_url, stream=True)
    if response.status_code == 200:
        with open(file_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
        print(f"Downloaded: {title}")
    else:
        print(f"Failed to download: {title}")


def download_podcast_episodes(feed_url, num_episodes=5):
    feed = feedparser.parse(feed_url)

    # Iterate over the entries in the feed
    for entry in feed.entries[:num_episodes]:
        title = entry.title
        media_url = entry.enclosures[0].href if entry.enclosures else None

        if media_url:
            download_episode(media_url, title)
        else:
            print(f"No media found for: {title}")


# Replace with the actual podcast RSS feed URL
podcast_feed_url = "https://your-podcast-feed-url.com/rss"
