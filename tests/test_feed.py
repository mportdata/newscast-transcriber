from modules.feed import Feed
from modules.episode import Episode
from datetime import date

FEED_URL = "https://feeds.libsyn.com/519643/rss"


def test_get_interview_episodes():
    # Arrange
    feed = Feed(FEED_URL)
    title = "The Benny the Butcher Interview with Throwing Fits"
    expected = Episode(
        title,
        "https://dts.podtrac.com/redirect.mp3/pscrb.fm/rss/p/traffic.libsyn.com/secure/79077014-187a-41fa-8c00-1d02e52704f6/APO9016431332.mp3?dest-id=4460808",
        date(2024, 1, 31),
    )

    # Act
    result = feed.get_interview_episodes(episode_limit=1)[title]

    # Assert
    assert result == expected
