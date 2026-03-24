# transcriber.py
import numpy as np
from faster_whisper import WhisperModel

COMPUTE_TYPES = {
    "cuda": "float16",
    "cpu": "int8",
}


class Transcriber:
    def __init__(self, model_size: str = "small", language: str = "de"):
        self._language = language
        self._model = self._load_model(model_size)

    def _load_model(self, model_size: str) -> WhisperModel:
        try:
            import torch
            device = "cuda" if torch.cuda.is_available() else "cpu"
        except ImportError:
            device = "cpu"
        compute_type = COMPUTE_TYPES.get(device, "int8")
        return WhisperModel(model_size, device=device, compute_type=compute_type)

    def transcribe(self, audio: np.ndarray) -> str:
        """Transkribiert numpy float32 Audio (16kHz Mono) zu Text."""
        if len(audio) == 0:
            return ""
        segments, _ = self._model.transcribe(
            audio,
            language=self._language,
            beam_size=5,
            vad_filter=True,
        )
        return " ".join(seg.text.strip() for seg in segments).strip()

    def reload(self, model_size: str, language: str) -> None:
        """Lädt ein neues Modell (nach Einstellungsänderung)."""
        self._language = language
        self._model = self._load_model(model_size)
