# tests/test_transcriber.py
import numpy as np
import pytest
from unittest.mock import patch, MagicMock
from transcriber import Transcriber


def test_transcribe_returns_string():
    with patch("transcriber.WhisperModel") as MockModel:
        mock_instance = MagicMock()
        mock_segment = MagicMock()
        mock_segment.text = " Hallo Welt"
        mock_instance.transcribe.return_value = ([mock_segment], MagicMock())
        MockModel.return_value = mock_instance

        t = Transcriber(model_size="small", language="de")
        audio = np.zeros(16000, dtype=np.float32)
        result = t.transcribe(audio)
        assert result == "Hallo Welt"


def test_transcribe_strips_whitespace():
    with patch("transcriber.WhisperModel") as MockModel:
        mock_instance = MagicMock()
        mock_segment = MagicMock()
        mock_segment.text = "  Text mit Leerzeichen  "
        mock_instance.transcribe.return_value = ([mock_segment], MagicMock())
        MockModel.return_value = mock_instance

        t = Transcriber(model_size="small", language="de")
        audio = np.zeros(16000, dtype=np.float32)
        result = t.transcribe(audio)
        assert result == "Text mit Leerzeichen"


def test_transcribe_empty_audio_returns_empty_string():
    with patch("transcriber.WhisperModel") as MockModel:
        mock_instance = MagicMock()
        mock_instance.transcribe.return_value = ([], MagicMock())
        MockModel.return_value = mock_instance

        t = Transcriber(model_size="small", language="de")
        audio = np.array([], dtype=np.float32)
        result = t.transcribe(audio)
        assert result == ""
