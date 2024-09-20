from pathlib import Path
from modules.episode import Episode
from modules.models import Transcriber, FitCheckExtractor
from datetime import date
import pytest

test_episode = Episode(
    "Test Episode",
    "https://eslyes.com/easydialogs/audio/dailylife001.mp3",
    date(2024, 1, 1),
)
audio_file_path = Path(f"podcasts/{test_episode.filename}.mp3")
transcript_file_path = Path(f"transcriptions/{test_episode.filename}.txt")
transcriber = Transcriber("tiny")
fit_check_extractor = FitCheckExtractor()


@pytest.fixture
def file_state_cleanup(request):
    # Record current state
    initial_download_status = test_episode.downloaded_status()
    initial_transcript_status = test_episode.transcribed_status()

    # Run Test
    yield

    # Clean up
    if test_episode.downloaded_status() and not initial_download_status:
        audio_file_path.unlink()
    if test_episode.transcribed_status() and not initial_transcript_status:
        transcript_file_path.unlink()


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
    assert response == True


def test_download_status_not_downloaded(file_state_cleanup):
    # Act
    if test_episode.downloaded_status():
        audio_file_path.unlink()
    response = test_episode.downloaded_status()

    # Assert
    assert response == False


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


def test_download_status_downloaded(file_state_cleanup):
    # Act
    test_episode.transcribe_episode(transcriber)
    response = test_episode.transcribed_status()

    # Assert
    assert response == True


def test_transcribe_status_not_transcribed(file_state_cleanup):
    # Act
    if test_episode.transcribed_status():
        audio_file_path.unlink()
    response = test_episode.downloaded_status()

    # Assert
    assert response == False


def test_get_transcription_text(file_state_cleanup):
    # Arrange
    expected_transcription_text = (
        "Where do you live? Where is Pasadena? It's in California. Is it in"
    )

    # Act
    transcription_text = test_episode.get_transcription_text(transcriber)

    # Assert
    assert transcription_text == expected_transcription_text


def test_extract_fit_check(file_state_cleanup):
    # Act
    test_episode.extract_fit_check(transcriber, fit_check_extractor)

    # Assert
    assert True
