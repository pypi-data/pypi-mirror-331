import os
from pathlib import Path

import pytest

from ak_transcribe.transcriber import *
from ak_transcribe.transcriber import TempMp3


# Define a temporary file for testing purposes
@pytest.fixture
def temp_file(tmpdir):
    # Create a dummy audio file in a temporary directory
    file_path = tmpdir / "test_audio.wav"
    file_path.write(
        "dummy data"
    )  # Writing some dummy data, actual content doesn't matter for these tests
    return Path(file_path)


def test_temp_mp3_conversion(tmpdir, temp_file):
    # Test the conversion of a non-MP3 file to MP3 using ffmpeg
    temp_mp3 = TempMp3(filepath=temp_file)
    with pytest.raises(
        Exception
    ):  # We expect an exception since we're trying to convert a dummy audio file
        with temp_mp3:
            pass  # The conversion should not succeed, and this line should never be reached


def test_temp_mp3_non_conversion(tmpdir, temp_file):
    # Test the scenario where the file is already an MP3 (no conversion should happen)
    temp_mp3 = TempMp3(
        filepath=Path("test.mp3")
    )  # Assume we have a real mp3 for testing
    with temp_mp3:
        assert isinstance(temp_mp3.mp3path, Path), "The path is not set correctly"
        assert temp_mp3.mp3path == Path(
            "test.mp3"
        ), "The path should be the same as the input file"
