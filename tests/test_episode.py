from pathlib import Path
from modules.episode import Episode
from modules.models import Transcriber
from datetime import datetime
import pytest

test_episode = Episode(
    "Test Channel",
    "Test Episode",
    "https://eslyes.com/easydialogs/audio/dailylife001.mp3",
    datetime(2024, 9, 21, 12, 30, 45),
)
audio_file_path = Path(
    f"podcasts/{test_episode.safe_channel_name}/{test_episode.safe_episode_name}.mp3"
)
transcript_file_path = Path(
    f"transcriptions/{test_episode.safe_channel_name}/{test_episode.safe_episode_name}.txt"
)
transcriber = Transcriber("tiny")


@pytest.fixture
def file_state_cleanup(request):
    # Record current state
    initial_download_status = test_episode.downloaded_status()
    initial_transcript_status = test_episode.transcribed_status()

    # Run Test
    yield

    # Clean up files
    if test_episode.downloaded_status() and not initial_download_status:
        audio_file_path.unlink()
    if test_episode.transcribed_status() and not initial_transcript_status:
        transcript_file_path.unlink()

    # Clean up directories if empty
    audio_directory = audio_file_path.parent
    transcript_directory = transcript_file_path.parent

    # Remove directories only if they are empty
    if audio_directory.exists() and not any(audio_directory.iterdir()):
        audio_directory.rmdir()
    if transcript_directory.exists() and not any(transcript_directory.iterdir()):
        transcript_directory.rmdir()


def test_download_episode(file_state_cleanup):
    # Act
    test_episode.download_episode()

    # Assert
    assert audio_file_path.exists(), f"File {audio_file_path} was not found."


def test_download_existing_episode(file_state_cleanup):
    # Arrange
    expected_response = {"status": "success", "message": "Episode already downloaded"}

    # Act
    test_episode.download_episode()
    response = test_episode.download_episode()

    # Assert
    assert response == expected_response


def test_download_status_downloaded(file_state_cleanup):
    # Act
    test_episode.download_episode()
    response = test_episode.downloaded_status()

    # Assert
    assert response is True


def test_download_status_not_downloaded(file_state_cleanup):
    # Act
    if test_episode.downloaded_status():
        audio_file_path.unlink()
    response = test_episode.downloaded_status()

    # Assert
    assert response is False


def test_transcribe_episode(file_state_cleanup):
    # Act
    test_episode.transcribe_episode(transcriber)

    # Assert
    assert transcript_file_path.exists(), f"File {transcript_file_path} was not found."


def test_transcribe_already_transcribed(file_state_cleanup):
    # Act
    test_episode.transcribe_episode(transcriber)
    response = test_episode.transcribe_episode(transcriber)

    # Assert
    assert response == {"status": "success", "message": "Episode already transcribed"}


def test_transcribe_status_transcribed(file_state_cleanup):
    # Act
    test_episode.transcribe_episode(transcriber)
    response = test_episode.transcribed_status()

    # Assert
    assert response is True


def test_transcribe_status_not_transcribed(file_state_cleanup):
    # Act
    if test_episode.transcribed_status():
        audio_file_path.unlink()
    response = test_episode.downloaded_status()

    # Assert
    assert response is False


def test_get_transcription_text(file_state_cleanup):
    # Arrange
    expected_transcription_text = "Where do you live? I live in Pasadena. Where is Pasadena? It's in California. Is it in Northern California? No. It's in Southern California. Is Pasadena a big city? It's pretty big. How big is pretty big? It has about 140,000.  People How big is Los Angeles? It has about 3 million people"

    # Act
    transcription_text = test_episode.get_transcription_text(transcriber)

    # Assert
    assert transcription_text == expected_transcription_text
