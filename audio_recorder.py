# audio_recorder.py
import threading
from typing import Optional, List, Tuple
import numpy as np
import sounddevice as sd

SAMPLE_RATE = 16000  # Whisper erwartet 16kHz


def list_microphones() -> List[Tuple[int, str]]:
    """Gibt Liste von (index, name) aller Eingabegeräte zurück."""
    devices = sd.query_devices()
    return [
        (i, d["name"])
        for i, d in enumerate(devices)
        if d["max_input_channels"] > 0
    ]


class AudioRecorder:
    def __init__(self, device_index: Optional[int] = None, sample_rate: int = SAMPLE_RATE):
        self._device_index = device_index
        self._sample_rate = sample_rate
        self._frames: List[np.ndarray] = []
        self._is_recording = False
        self._stream: Optional[sd.InputStream] = None
        self._lock = threading.Lock()

    @property
    def is_recording(self) -> bool:
        return self._is_recording

    def start(self) -> None:
        """Startet Audioaufnahme."""
        with self._lock:
            if self._is_recording:
                return
            self._frames = []
            self._is_recording = True
            self._stream = sd.InputStream(
                samplerate=self._sample_rate,
                channels=1,
                dtype="float32",
                device=self._device_index,
                callback=self._callback,
            )
            self._stream.start()

    def stop(self) -> np.ndarray:
        """Stoppt Aufnahme und gibt gesammeltes Audio als numpy-Array zurück."""
        with self._lock:
            if not self._is_recording:
                return np.array([], dtype=np.float32)
            self._is_recording = False
            if self._stream:
                self._stream.stop()
                self._stream.close()
                self._stream = None
            if not self._frames:
                return np.array([], dtype=np.float32)
            audio = np.concatenate(self._frames, axis=0).flatten()
            self._frames = []
            return audio

    def _callback(self, indata: np.ndarray, frames: int, time, status) -> None:
        if self._is_recording:
            self._frames.append(indata.copy())
