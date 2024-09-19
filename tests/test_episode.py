from pathlib import Path
from modules.episode import Episode
from datetime import date


def test_download_episode():
    # Arrange
    episode = Episode(
        "The Benny the Butcher Interview with Throwing Fits",
        "https://dts.podtrac.com/redirect.mp3/pscrb.fm/rss/p/traffic.libsyn.com/secure/79077014-187a-41fa-8c00-1d02e52704f6/APO9016431332.mp3?dest-id=4460808",
        date(2024, 1, 31),
    )
    expected_file_path = Path(f"podcasts/{episode.filename}.mp3")

    # Act
    episode.download_episode()

    # Assert
    assert expected_file_path.exists(), f"File {expected_file_path} was not found."

    # Clean up
    if expected_file_path.exists():
        expected_file_path.unlink()
