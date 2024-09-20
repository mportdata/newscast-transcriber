import unittest
from modules.models import Transcriber, FitCheckExtractor


def test_transcriber_init():
    # Act
    transcriber = Transcriber("tiny")

    # Assert
    assert (
        (transcriber.processor != None)
        and (transcriber.model != None)
        and (transcriber.device in ["cpu", "gpu"])
    )


def test_fit_check_extractor_init():
    # Act
    fit_check_extractor = FitCheckExtractor()

    # Assert
    assert fit_check_extractor != None
