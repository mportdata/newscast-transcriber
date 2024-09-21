from modules.models import Transcriber


def test_transcriber_init():
    # Act
    transcriber = Transcriber("tiny")

    # Assert
    assert (
        (transcriber.processor is not None)
        and (transcriber.model is not None)
        and (transcriber.device in ["cpu", "gpu"])
    )
