# tests/test_audio_recorder.py
import numpy as np
import pytest
from unittest.mock import patch, MagicMock
from audio_recorder import AudioRecorder


def test_start_sets_recording_flag():
    recorder = AudioRecorder(device_index=None, sample_rate=16000)
    with patch("sounddevice.InputStream") as mock_stream_cls:
        mock_stream = MagicMock()
        mock_stream_cls.return_value = mock_stream
        recorder.start()
        assert recorder.is_recording is True
        recorder.stop()


def test_stop_returns_numpy_array():
    recorder = AudioRecorder(device_index=None, sample_rate=16000)
    # Simuliere bereits gesammelte Audio-Daten
    recorder._frames = [np.zeros((1024, 1), dtype=np.float32)]
    recorder._is_recording = True
    result = recorder.stop()
    assert isinstance(result, np.ndarray)
    assert result.dtype == np.float32


def test_stop_without_start_returns_empty():
    recorder = AudioRecorder(device_index=None, sample_rate=16000)
    result = recorder.stop()
    assert isinstance(result, np.ndarray)
    assert len(result) == 0


def test_list_microphones_returns_list():
    from audio_recorder import list_microphones
    mics = list_microphones()
    assert isinstance(mics, list)
