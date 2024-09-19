from modules.ingest import get_episode_data_from_feed, download_episode
from unittest.mock import patch
from datetime import date
import pytest
import os
from pathlib import Path

FEED_URL = "https://feeds.libsyn.com/519643/rss"


def test_get_episode_data_from_feed():
    # Arrage
    feed_url = FEED_URL
    expected = {
        "The Benny the Butcher Interview with Throwing Fits": {
            "release_date": date(2024, 1, 31),
            "url": "https://dts.podtrac.com/redirect.mp3/pscrb.fm/rss/p/traffic.libsyn.com/secure/79077014-187a-41fa-8c00-1d02e52704f6/APO9016431332.mp3?dest-id=4460808",
        }
    }

    # Act
    result = get_episode_data_from_feed(feed_url, episode_limit=1)
    print(result)

    # Assert
    assert result == expected


def test_download_episode():
    # Arrange
    episode_title = "The Benny the Butcher Interview with Throwing Fits"
    file_name = "".join([c if c.isalnum() else "_" for c in episode_title]) + ".mp3"
    episode_url = "https://dts.podtrac.com/redirect.mp3/pscrb.fm/rss/p/traffic.libsyn.com/secure/79077014-187a-41fa-8c00-1d02e52704f6/APO9016431332.mp3?dest-id=4460808"
    expected_file_path = Path(f"podcasts/{file_name}")

    # Act
    download_episode(episode_title, episode_url)

    # Assert
    assert expected_file_path.exists(), f"File {expected_file_path} was not found."

    # Clean up
    if expected_file_path.exists():
        expected_file_path.unlink()
