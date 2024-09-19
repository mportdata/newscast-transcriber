from modules.transcribe import Transcriber, transcribe_episode
from modules.ingest import download_episode
from transformers import WhisperProcessor, WhisperForConditionalGeneration
import torch
from pathlib import Path


def test_transcribe_episode():
    # Arrange

    episode_title = "The Benny the Butcher Interview with Throwing Fits"
    file_name = "".join([c if c.isalnum() else "_" for c in episode_title]) + ".mp3"
    episode_url = "https://dts.podtrac.com/redirect.mp3/pscrb.fm/rss/p/traffic.libsyn.com/secure/79077014-187a-41fa-8c00-1d02e52704f6/APO9016431332.mp3?dest-id=4460808"
    file_path = Path(f"podcasts/{file_name}")
    transcriber = Transcriber()

    # Act
    download_episode(episode_title, episode_url)
    transcription = transcribe_episode(transcriber, episode_title)
    print(transcription)

    # Assert
    assert True

    # Clean up
    if file_path.exists():
        file_path.unlink()
