# settings.py
import json
import os
from dataclasses import dataclass, asdict
from typing import Optional

APPDATA_DIR = os.path.join(os.environ.get("APPDATA", ""), "TranskriptionLokal")
CONFIG_PATH = os.path.join(APPDATA_DIR, "config.json")

AVAILABLE_MODELS = ["tiny", "base", "small", "medium", "large-v2", "large-v3"]
AVAILABLE_LANGUAGES = [
    ("Deutsch", "de"),
    ("English", "en"),
    ("Français", "fr"),
    ("Español", "es"),
    ("Italiano", "it"),
    ("Português", "pt"),
    ("Nederlands", "nl"),
    ("Polski", "pl"),
    ("Русский", "ru"),
    ("中文", "zh"),
    ("日本語", "ja"),
]
HOTKEY_MODES = [("Halten", "hold"), ("Umschalten", "toggle")]


@dataclass
class Settings:
    hotkey: str = "f12"
    hotkey_mode: str = "hold"
    model: str = "small"
    language: str = "de"
    microphone_index: Optional[int] = None

    def save(self) -> None:
        os.makedirs(APPDATA_DIR, exist_ok=True)
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(asdict(self), f, indent=2)

    @classmethod
    def load(cls) -> "Settings":
        defaults = asdict(cls())
        if not os.path.exists(CONFIG_PATH):
            return cls()
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
            merged = {**defaults, **data}
            return cls(**{k: merged[k] for k in defaults})
        except (json.JSONDecodeError, TypeError):
            return cls()
