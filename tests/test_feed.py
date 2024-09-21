from modules.feed import Feed

feed_url_dict = {
    "Fox News Hourly Update": "https://feeds.megaphone.fm/FOXM2252206613",
    "CNN Breaking News Alerts": "https://feeds.megaphone.fm/WMHY6108281879",
    "NPR News": "https://feeds.npr.org/500005/podcast.xml",
    "BBC Minute": "http://wsrss.bbc.co.uk/bizdev/bbcminute/bbcminute.rss",
}


def test_feed_init():
    # Arrange
    expected_feed_url_dict = feed_url_dict

    # Act
    response_feed_url_dict = {}
    for feed_url_name in feed_url_dict:
        feed = Feed(feed_url_name, feed_url_dict[feed_url_name])
        response_feed_url_dict[feed.name] = feed.url

    # Assert
    assert response_feed_url_dict == expected_feed_url_dict


def test_get_latest_episode():
    # Arrange
    expected_feed_url_dict = feed_url_dict
    episode_dict = {}

    # Act
    for feed_url_name in feed_url_dict:
        feed = Feed(feed_url_name, feed_url_dict[feed_url_name])
        episode = feed.get_latest_episode()
        episode_dict[feed_url_name] = episode

    # Assert
    assert all(
        episode_dict[episode_url_name].channel_name == episode_url_name
        for episode_url_name in expected_feed_url_dict
    )
