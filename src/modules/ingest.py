import feedparser
import requests
import os


# Step 1: Parse the podcast RSS feed
def parse_podcast_feed(feed_url):
    return feedparser.parse(feed_url)


# Step 2: Download the podcast episode from the feed entry
def download_episode(episode_url, title, save_dir="podcasts"):
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


# Step 3: Process the feed and download all episodes
def download_podcast_episodes(feed_url, num_episodes=5):
    feed = parse_podcast_feed(feed_url)

    # Iterate over the entries in the feed
    for entry in feed.entries[:num_episodes]:
        title = entry.title
        media_url = entry.enclosures[0].href if entry.enclosures else None

        if media_url:
            download_episode(media_url, title)
        else:
            print(f"No media found for: {title}")


# Example usage
if __name__ == "__main__":
    # Replace with the actual podcast RSS feed URL
    podcast_feed_url = "https://your-podcast-feed-url.com/rss"

    # Download the first 5 episodes (you can adjust the number)
    download_podcast_episodes(podcast_feed_url, num_episodes=5)
