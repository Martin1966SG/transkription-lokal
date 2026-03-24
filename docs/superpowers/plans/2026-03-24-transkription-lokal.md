# TranskriptionLokal Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Windows-Tray-Applikation, die per konfigurierbarem Hotkey (Standard: F12 halten) Sprache aufnimmt, lokal mit faster-whisper transkribiert und den Text in das aktuell aktive Textfeld einfügt — ohne sichtbares Hauptfenster.

**Architecture:** pystray läuft auf dem Hauptthread (Windows-Pflicht). pynput verwaltet seinen eigenen Listener-Thread für Hotkey-Erkennung. Audioaufnahme und Transkription laufen in separaten Worker-Threads. Ein zentrales `App`-Objekt hält den Zustand (IDLE → RECORDING → PROCESSING → IDLE) und koordiniert alle Komponenten. Einstellungen werden in `%APPDATA%\TranskriptionLokal\config.json` gespeichert.

**Tech Stack:** Python 3.10+, faster-whisper, pynput, pystray, sounddevice, numpy, Pillow, pyperclip, tkinter (built-in), ctypes (built-in)

---

## Dateistruktur

```
TranskriptionLokal/
├── main.py                   # Einstiegspunkt, startet App
├── app.py                    # Zustandsmaschine & Koordinator
├── settings.py               # Einstellungen laden/speichern (JSON)
├── settings_dialog.py        # Tkinter-Einstellungsdialog
├── audio_recorder.py         # Audioaufnahme via sounddevice
├── transcriber.py            # Transkription via faster-whisper
├── text_inserter.py          # Text einfügen via Clipboard + Ctrl+V
├── hotkey_handler.py         # Hotkey-Listener via pynput
├── tray_icon.py              # Tray-Icon & Kontextmenü via pystray
├── notification.py           # Rote Fehler-Benachrichtigung (tkinter-Popup)
├── icons.py                  # Programmatische Icon-Generierung (Pillow)
├── requirements.txt
└── tests/
    ├── test_settings.py
    ├── test_audio_recorder.py
    ├── test_transcriber.py
    └── test_text_inserter.py
```

### Verantwortlichkeiten

| Datei | Verantwortung |
|---|---|
| `main.py` | Einstiegspunkt, App-Instanz erstellen und starten |
| `app.py` | Zustandsmaschine (IDLE/RECORDING/PROCESSING), alle Komponenten verdrahten |
| `settings.py` | Dataclass für Einstellungen, JSON-Persistenz in %APPDATA% |
| `settings_dialog.py` | Tkinter-Modal: Mikrofon, Hotkey, Modell, Sprache, Hotkey-Modus |
| `audio_recorder.py` | sounddevice-Aufnahme starten/stoppen, numpy-Array zurückgeben |
| `transcriber.py` | faster-whisper laden (GPU/CPU), Audio transkribieren |
| `text_inserter.py` | Clipboard speichern, Text einfügen, Clipboard wiederherstellen |
| `hotkey_handler.py` | pynput-Listener, Hold-Modus und Toggle-Modus, konfigurierbarer Key |
| `tray_icon.py` | pystray-Icon in 3 Zuständen (idle/recording/processing), Kontextmenü |
| `notification.py` | Rotes Tkinter-Popup, erscheint unten rechts, schließt nach N Sekunden |
| `icons.py` | Pillow-generierte Icons: grün (idle), rot (recording), gelb (processing) |

---

## Task 1: Projekt-Setup

**Files:**
- Create: `requirements.txt`
- Create: `tests/__init__.py`

- [ ] **Step 1: requirements.txt erstellen**

```
faster-whisper>=1.0.0
pynput>=1.7.6
pystray>=0.19.4
sounddevice>=0.4.6
numpy>=1.24.0
Pillow>=10.0.0
pyperclip>=1.8.2
```

- [ ] **Step 2: Abhängigkeiten installieren**

```bash
pip install -r requirements.txt
```

Erwartete Ausgabe: Alle Pakete installiert ohne Fehler.

- [ ] **Step 3: Verzeichnisse anlegen**

```bash
mkdir tests
touch tests/__init__.py
```

- [ ] **Step 4: Python-Version prüfen**

```bash
python --version
```

Erwartete Ausgabe: `Python 3.10.x` oder höher.

- [ ] **Step 5: GPU-Verfügbarkeit prüfen**

```python
# Kurzer Check in Python-Shell
import torch
print(torch.cuda.is_available())
```

Hinweis: Falls `torch` nicht installiert ist, wird faster-whisper CTranslate2 direkt nutzen. Das ist OK.

- [ ] **Step 6: Commit**

```bash
git add requirements.txt tests/__init__.py
git commit -m "chore: project setup with dependencies"
```

---

## Task 2: Einstellungen (settings.py)

**Files:**
- Create: `settings.py`
- Create: `tests/test_settings.py`

### Einstellungsfelder

| Feld | Typ | Default |
|---|---|---|
| `hotkey` | str | `"f12"` |
| `hotkey_mode` | str | `"hold"` (oder `"toggle"`) |
| `model` | str | `"small"` |
| `language` | str | `"de"` |
| `microphone_index` | int oder None | `None` (Standardmikrofon) |

- [ ] **Step 1: Failing Tests schreiben**

```python
# tests/test_settings.py
import os
import json
import tempfile
import pytest
from unittest.mock import patch
from settings import Settings, APPDATA_DIR

def test_default_values():
    s = Settings()
    assert s.hotkey == "f12"
    assert s.hotkey_mode == "hold"
    assert s.model == "small"
    assert s.language == "de"
    assert s.microphone_index is None

def test_save_and_load(tmp_path):
    config_path = tmp_path / "config.json"
    with patch("settings.CONFIG_PATH", str(config_path)):
        s = Settings(hotkey="f11", model="medium")
        s.save()
        loaded = Settings.load()
        assert loaded.hotkey == "f11"
        assert loaded.model == "medium"

def test_load_returns_defaults_when_no_file(tmp_path):
    config_path = tmp_path / "nonexistent.json"
    with patch("settings.CONFIG_PATH", str(config_path)):
        s = Settings.load()
        assert s.hotkey == "f12"

def test_load_merges_missing_keys(tmp_path):
    """Neue Felder in späteren Versionen haben defaults, auch wenn config-Datei alt ist."""
    config_path = tmp_path / "config.json"
    config_path.write_text(json.dumps({"hotkey": "f10"}))
    with patch("settings.CONFIG_PATH", str(config_path)):
        s = Settings.load()
        assert s.hotkey == "f10"
        assert s.model == "small"  # Default, weil nicht in alter config
```

- [ ] **Step 2: Tests ausführen und Fehler bestätigen**

```bash
pytest tests/test_settings.py -v
```

Erwartete Ausgabe: `ImportError` oder `ModuleNotFoundError`.

- [ ] **Step 3: settings.py implementieren**

```python
# settings.py
import json
import os
from dataclasses import dataclass, asdict, field
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
```

- [ ] **Step 4: Tests ausführen und Erfolg bestätigen**

```bash
pytest tests/test_settings.py -v
```

Erwartete Ausgabe: Alle Tests `PASSED`.

- [ ] **Step 5: Commit**

```bash
git add settings.py tests/test_settings.py
git commit -m "feat: settings dataclass with JSON persistence in APPDATA"
```

---

## Task 3: Icon-Generierung (icons.py)

**Files:**
- Create: `icons.py`

Keine Unit-Tests nötig (reine Pillow-Bildgenerierung, visuell zu prüfen).

- [ ] **Step 1: icons.py implementieren**

```python
# icons.py
from PIL import Image, ImageDraw

ICON_SIZE = (64, 64)


def _make_circle_icon(color: str, bg_color: str = "#2b2b2b") -> Image.Image:
    img = Image.new("RGBA", ICON_SIZE, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    margin = 6
    draw.ellipse(
        [margin, margin, ICON_SIZE[0] - margin, ICON_SIZE[1] - margin],
        fill=color,
        outline=bg_color,
        width=2,
    )
    return img


def get_idle_icon() -> Image.Image:
    """Grüner Kreis — bereit."""
    return _make_circle_icon("#4caf50")


def get_recording_icon() -> Image.Image:
    """Roter Kreis — Aufnahme läuft."""
    return _make_circle_icon("#f44336")


def get_processing_icon() -> Image.Image:
    """Gelber Kreis — Transkription läuft."""
    return _make_circle_icon("#ff9800")
```

- [ ] **Step 2: Visuell prüfen**

```python
# Kurzer Check in Python-Shell
from icons import get_idle_icon, get_recording_icon, get_processing_icon
get_idle_icon().show()
get_recording_icon().show()
get_processing_icon().show()
```

Erwartete Ausgabe: Drei Fenster mit grünem, rotem und gelbem Kreis.

- [ ] **Step 3: Commit**

```bash
git add icons.py
git commit -m "feat: programmatic tray icon generation (idle/recording/processing)"
```

---

## Task 4: Fehler-Benachrichtigung (notification.py)

**Files:**
- Create: `notification.py`

Keine automatisierten Tests (tkinter-UI). Manuell testen.

- [ ] **Step 1: notification.py implementieren**

```python
# notification.py
import tkinter as tk
import threading


def show_error(message: str, duration_ms: int = 4000) -> None:
    """Zeigt ein rotes Fehler-Popup unten rechts an, das sich nach `duration_ms` ms schließt.
    Läuft in eigenem Thread, um den Aufrufer nicht zu blockieren."""
    t = threading.Thread(target=_show, args=(message, duration_ms), daemon=True)
    t.start()


def _show(message: str, duration_ms: int) -> None:
    root = tk.Tk()
    root.overrideredirect(True)       # Kein Fensterrahmen
    root.attributes("-topmost", True) # Immer im Vordergrund
    root.configure(bg="#c62828")

    label = tk.Label(
        root,
        text=message,
        bg="#c62828",
        fg="white",
        font=("Segoe UI", 10, "bold"),
        wraplength=280,
        justify="left",
        padx=12,
        pady=10,
    )
    label.pack()

    root.update_idletasks()
    w = root.winfo_width()
    h = root.winfo_height()
    screen_w = root.winfo_screenwidth()
    screen_h = root.winfo_screenheight()
    # Taskbar-Höhe ca. 48px einrechnen
    x = screen_w - w - 16
    y = screen_h - h - 64
    root.geometry(f"+{x}+{y}")

    root.after(duration_ms, root.destroy)
    root.mainloop()
```

- [ ] **Step 2: Manuell testen**

```python
# Python-Shell
from notification import show_error
import time
show_error("Kein Mikrofon gefunden!")
time.sleep(5)  # Popup sollte nach 4s verschwinden
```

- [ ] **Step 3: Commit**

```bash
git add notification.py
git commit -m "feat: red error notification popup (auto-close)"
```

---

## Task 5: Audio-Aufnahme (audio_recorder.py)

**Files:**
- Create: `audio_recorder.py`
- Create: `tests/test_audio_recorder.py`

- [ ] **Step 1: Failing Tests schreiben**

```python
# tests/test_audio_recorder.py
import numpy as np
import pytest
from unittest.mock import patch, MagicMock
from audio_recorder import AudioRecorder


def test_start_sets_recording_flag():
    recorder = AudioRecorder(device_index=None, sample_rate=16000)
    with patch("sounddevice.InputStream") as mock_stream:
        mock_stream.return_value.__enter__ = MagicMock(return_value=mock_stream.return_value)
        mock_stream.return_value.__exit__ = MagicMock(return_value=False)
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
```

- [ ] **Step 2: Tests ausführen und Fehler bestätigen**

```bash
pytest tests/test_audio_recorder.py -v
```

- [ ] **Step 3: audio_recorder.py implementieren**

```python
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
        """Startet Audioaufnahme in eigenem Thread."""
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
```

- [ ] **Step 4: Tests ausführen**

```bash
pytest tests/test_audio_recorder.py -v
```

Erwartete Ausgabe: Alle Tests `PASSED`.

- [ ] **Step 5: Commit**

```bash
git add audio_recorder.py tests/test_audio_recorder.py
git commit -m "feat: audio recorder with sounddevice, start/stop/list_microphones"
```

---

## Task 6: Transkription (transcriber.py)

**Files:**
- Create: `transcriber.py`
- Create: `tests/test_transcriber.py`

- [ ] **Step 1: Failing Tests schreiben**

```python
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
```

- [ ] **Step 2: Tests ausführen und Fehler bestätigen**

```bash
pytest tests/test_transcriber.py -v
```

- [ ] **Step 3: transcriber.py implementieren**

```python
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
```

- [ ] **Step 4: Tests ausführen**

```bash
pytest tests/test_transcriber.py -v
```

Erwartete Ausgabe: Alle Tests `PASSED`.

- [ ] **Step 5: Commit**

```bash
git add transcriber.py tests/test_transcriber.py
git commit -m "feat: faster-whisper transcriber with GPU/CPU auto-detection"
```

---

## Task 7: Text-Einfügen (text_inserter.py)

**Files:**
- Create: `text_inserter.py`
- Create: `tests/test_text_inserter.py`

- [ ] **Step 1: Failing Tests schreiben**

```python
# tests/test_text_inserter.py
import pytest
from unittest.mock import patch, call
from text_inserter import insert_text


def test_insert_text_saves_and_restores_clipboard():
    with patch("pyperclip.copy") as mock_copy, \
         patch("pyperclip.paste", return_value="original content"), \
         patch("text_inserter._simulate_paste") as mock_paste, \
         patch("time.sleep"):

        insert_text("transkribierter Text")

        # Zuerst: Original Clipboard lesen (passiert implizit durch paste())
        # Dann: Neuen Text in Clipboard setzen
        assert call("transkribierter Text") in mock_copy.call_args_list
        # Dann: Einfügen simulieren
        mock_paste.assert_called_once()
        # Dann: Original wiederherstellen
        assert call("original content") in mock_copy.call_args_list


def test_insert_text_empty_string_does_nothing():
    with patch("pyperclip.copy") as mock_copy, \
         patch("pyperclip.paste", return_value="original"), \
         patch("text_inserter._simulate_paste") as mock_paste:

        insert_text("")
        mock_paste.assert_not_called()
```

- [ ] **Step 2: Tests ausführen und Fehler bestätigen**

```bash
pytest tests/test_text_inserter.py -v
```

- [ ] **Step 3: text_inserter.py implementieren**

```python
# text_inserter.py
import time
import pyperclip
from pynput.keyboard import Controller, Key

_keyboard = Controller()


def _simulate_paste() -> None:
    """Simuliert Ctrl+V Tastenkombination."""
    _keyboard.press(Key.ctrl)
    _keyboard.press("v")
    time.sleep(0.05)
    _keyboard.release("v")
    _keyboard.release(Key.ctrl)


def insert_text(text: str) -> None:
    """Fügt Text in das aktive Textfeld ein.

    Speichert vorherigen Clipboard-Inhalt und stellt ihn danach wieder her.
    """
    if not text:
        return

    original = pyperclip.paste()
    try:
        pyperclip.copy(text)
        time.sleep(0.1)  # Kurz warten bis Clipboard bereit ist
        _simulate_paste()
        time.sleep(0.15)  # Warten bis Einfügen abgeschlossen ist
    finally:
        pyperclip.copy(original)
```

- [ ] **Step 4: Tests ausführen**

```bash
pytest tests/test_text_inserter.py -v
```

Erwartete Ausgabe: Alle Tests `PASSED`.

- [ ] **Step 5: Commit**

```bash
git add text_inserter.py tests/test_text_inserter.py
git commit -m "feat: text inserter via clipboard with original content restore"
```

---

## Task 8: Hotkey-Handler (hotkey_handler.py)

**Files:**
- Create: `hotkey_handler.py`

Keine automatisierten Unit-Tests (pynput-Listener schwer zu mocken). Integration wird in app.py getestet.

- [ ] **Step 1: hotkey_handler.py implementieren**

```python
# hotkey_handler.py
import threading
from typing import Callable, Optional
from pynput import keyboard
from pynput.keyboard import Key, KeyCode


def _parse_key(hotkey_str: str):
    """Konvertiert z.B. 'f12' → pynput Key.f12 oder KeyCode."""
    hotkey_str = hotkey_str.lower()
    # Versuche als Special Key (f1-f12, etc.)
    try:
        return getattr(Key, hotkey_str)
    except AttributeError:
        pass
    # Fallback: einzelner Buchstabe/Zeichen
    if len(hotkey_str) == 1:
        return KeyCode.from_char(hotkey_str)
    return None


class HotkeyHandler:
    """Lauscht auf einen konfigurierbaren Hotkey.

    Modi:
    - 'hold': on_press beim Drücken, on_release beim Loslassen
    - 'toggle': on_press beim ersten Drücken, on_release beim zweiten Drücken
    """

    def __init__(
        self,
        hotkey: str,
        mode: str,
        on_press: Callable[[], None],
        on_release: Callable[[], None],
    ):
        self._target_key = _parse_key(hotkey)
        self._mode = mode
        self._on_press = on_press
        self._on_release = on_release
        self._toggled = False
        self._listener: Optional[keyboard.Listener] = None

    def start(self) -> None:
        self._listener = keyboard.Listener(
            on_press=self._handle_press,
            on_release=self._handle_release,
        )
        self._listener.start()

    def stop(self) -> None:
        if self._listener:
            self._listener.stop()
            self._listener = None

    def _handle_press(self, key) -> None:
        if key != self._target_key:
            return
        if self._mode == "hold":
            self._on_press()
        elif self._mode == "toggle" and not self._toggled:
            self._toggled = True
            self._on_press()

    def _handle_release(self, key) -> None:
        if key != self._target_key:
            return
        if self._mode == "hold":
            self._on_release()
        elif self._mode == "toggle" and self._toggled:
            self._toggled = False
            self._on_release()
```

- [ ] **Step 2: Manuell prüfen**

```python
# Python-Shell
from hotkey_handler import HotkeyHandler
import time

h = HotkeyHandler("f12", "hold",
    on_press=lambda: print("PRESS"),
    on_release=lambda: print("RELEASE"))
h.start()
time.sleep(10)  # F12 mehrmals drücken und loslassen
h.stop()
```

- [ ] **Step 3: Commit**

```bash
git add hotkey_handler.py
git commit -m "feat: configurable hotkey handler with hold and toggle modes"
```

---

## Task 9: Einstellungsdialog (settings_dialog.py)

**Files:**
- Create: `settings_dialog.py`

- [ ] **Step 1: settings_dialog.py implementieren**

```python
# settings_dialog.py
import tkinter as tk
from tkinter import ttk
from typing import Callable, List, Tuple
import sounddevice as sd
from settings import Settings, AVAILABLE_MODELS, AVAILABLE_LANGUAGES, HOTKEY_MODES
from audio_recorder import list_microphones

AVAILABLE_HOTKEYS = [
    "f1", "f2", "f3", "f4", "f5", "f6",
    "f7", "f8", "f9", "f10", "f11", "f12",
]


class SettingsDialog:
    def __init__(self, settings: Settings, on_save: Callable[[Settings], None]):
        self._settings = settings
        self._on_save = on_save

    def show(self) -> None:
        """Öffnet den Einstellungsdialog modal."""
        root = tk.Tk()
        root.title("TranskriptionLokal – Einstellungen")
        root.resizable(False, False)
        root.attributes("-topmost", True)

        pad = {"padx": 10, "pady": 5}

        # Mikrofon
        tk.Label(root, text="Mikrofon:").grid(row=0, column=0, sticky="w", **pad)
        mics = list_microphones()
        mic_options = ["Standard"] + [name for _, name in mics]
        mic_var = tk.StringVar()
        mic_box = ttk.Combobox(root, textvariable=mic_var, values=mic_options,
                               state="readonly", width=35)
        mic_box.grid(row=0, column=1, **pad)
        if self._settings.microphone_index is None:
            mic_var.set("Standard")
        else:
            idx = self._settings.microphone_index
            mic_var.set(mics[idx][1] if idx < len(mics) else "Standard")

        # Hotkey
        tk.Label(root, text="Hotkey:").grid(row=1, column=0, sticky="w", **pad)
        hotkey_var = tk.StringVar(value=self._settings.hotkey)
        hotkey_box = ttk.Combobox(root, textvariable=hotkey_var,
                                  values=AVAILABLE_HOTKEYS, state="readonly", width=10)
        hotkey_box.grid(row=1, column=1, sticky="w", **pad)

        # Hotkey-Modus
        tk.Label(root, text="Hotkey-Modus:").grid(row=2, column=0, sticky="w", **pad)
        mode_var = tk.StringVar(value=self._settings.hotkey_mode)
        for i, (label, value) in enumerate(HOTKEY_MODES):
            tk.Radiobutton(root, text=label, variable=mode_var,
                           value=value).grid(row=2, column=1+i, sticky="w", **pad)

        # Modell
        tk.Label(root, text="Whisper-Modell:").grid(row=3, column=0, sticky="w", **pad)
        model_var = tk.StringVar(value=self._settings.model)
        model_box = ttk.Combobox(root, textvariable=model_var,
                                 values=AVAILABLE_MODELS, state="readonly", width=15)
        model_box.grid(row=3, column=1, sticky="w", **pad)

        # Sprache
        tk.Label(root, text="Sprache:").grid(row=4, column=0, sticky="w", **pad)
        lang_names = [name for name, _ in AVAILABLE_LANGUAGES]
        lang_codes = [code for _, code in AVAILABLE_LANGUAGES]
        lang_var = tk.StringVar()
        lang_box = ttk.Combobox(root, textvariable=lang_var,
                                values=lang_names, state="readonly", width=15)
        lang_box.grid(row=4, column=1, sticky="w", **pad)
        current_lang_idx = lang_codes.index(self._settings.language) \
            if self._settings.language in lang_codes else 0
        lang_var.set(lang_names[current_lang_idx])

        def save():
            selected_mic = mic_var.get()
            mic_index = None
            if selected_mic != "Standard":
                matches = [i for i, name in mics if name == selected_mic]
                mic_index = matches[0] if matches else None

            lang_name = lang_var.get()
            lang_code = lang_codes[lang_names.index(lang_name)] \
                if lang_name in lang_names else "de"

            new_settings = Settings(
                hotkey=hotkey_var.get(),
                hotkey_mode=mode_var.get(),
                model=model_var.get(),
                language=lang_code,
                microphone_index=mic_index,
            )
            new_settings.save()
            self._on_save(new_settings)
            root.destroy()

        def cancel():
            root.destroy()

        btn_frame = tk.Frame(root)
        btn_frame.grid(row=5, column=0, columnspan=3, pady=10)
        tk.Button(btn_frame, text="Speichern", command=save, width=12).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Abbrechen", command=cancel, width=12).pack(side="left", padx=5)

        root.mainloop()
```

- [ ] **Step 2: Manuell testen**

```python
# Python-Shell
from settings import Settings
from settings_dialog import SettingsDialog

def on_save(s):
    print("Gespeichert:", s)

d = SettingsDialog(Settings(), on_save)
d.show()
```

Prüfen: Dialog öffnet sich, alle Felder sind korrekt befüllt, Speichern schreibt config.json.

- [ ] **Step 3: Commit**

```bash
git add settings_dialog.py
git commit -m "feat: settings dialog with mic, hotkey, model, language selection"
```

---

## Task 10: Tray-Icon (tray_icon.py)

**Files:**
- Create: `tray_icon.py`

- [ ] **Step 1: tray_icon.py implementieren**

```python
# tray_icon.py
from typing import Callable
import pystray
from pystray import MenuItem as Item
from icons import get_idle_icon, get_recording_icon, get_processing_icon

APP_NAME = "TranskriptionLokal"


class TrayIcon:
    def __init__(
        self,
        on_settings: Callable[[], None],
        on_quit: Callable[[], None],
    ):
        self._on_settings = on_settings
        self._on_quit = on_quit
        self._icon = pystray.Icon(
            APP_NAME,
            icon=get_idle_icon(),
            title=APP_NAME,
            menu=pystray.Menu(
                Item("Einstellungen", self._settings_clicked),
                Item("Beenden", self._quit_clicked),
            ),
        )

    def run(self) -> None:
        """Startet das Tray-Icon (blockierend — muss auf dem Hauptthread laufen)."""
        self._icon.run()

    def stop(self) -> None:
        self._icon.stop()

    def set_idle(self) -> None:
        self._icon.icon = get_idle_icon()
        self._icon.title = APP_NAME

    def set_recording(self) -> None:
        self._icon.icon = get_recording_icon()
        self._icon.title = f"{APP_NAME} – Aufnahme läuft..."

    def set_processing(self) -> None:
        self._icon.icon = get_processing_icon()
        self._icon.title = f"{APP_NAME} – Verarbeitung..."

    def _settings_clicked(self, icon, item) -> None:
        self._on_settings()

    def _quit_clicked(self, icon, item) -> None:
        self._on_quit()
```

- [ ] **Step 2: Manuell testen**

```python
# Python-Shell — Ctrl+C zum Beenden
from tray_icon import TrayIcon
import time, threading

def on_settings(): print("Einstellungen geklickt")
def on_quit(): print("Beenden geklickt"); tray.stop()

tray = TrayIcon(on_settings, on_quit)

# Icon-Wechsel nach 3s testen
def cycle():
    time.sleep(3); tray.set_recording()
    time.sleep(3); tray.set_processing()
    time.sleep(3); tray.set_idle()

threading.Thread(target=cycle, daemon=True).start()
tray.run()
```

Prüfen: Icon wechselt zwischen grün/rot/gelb; Kontextmenü zeigt "Einstellungen" und "Beenden".

- [ ] **Step 3: Commit**

```bash
git add tray_icon.py
git commit -m "feat: tray icon with 3 states and context menu"
```

---

## Task 11: App-Orchestrator (app.py)

**Files:**
- Create: `app.py`

- [ ] **Step 1: app.py implementieren**

```python
# app.py
import threading
from enum import Enum, auto
from settings import Settings
from settings_dialog import SettingsDialog
from audio_recorder import AudioRecorder
from transcriber import Transcriber
from text_inserter import insert_text
from hotkey_handler import HotkeyHandler
from tray_icon import TrayIcon
from notification import show_error


class State(Enum):
    IDLE = auto()
    RECORDING = auto()
    PROCESSING = auto()


class App:
    def __init__(self):
        self._settings = Settings.load()
        self._state = State.IDLE
        self._lock = threading.Lock()

        self._recorder = AudioRecorder(
            device_index=self._settings.microphone_index
        )
        self._transcriber = Transcriber(
            model_size=self._settings.model,
            language=self._settings.language,
        )
        self._hotkey = HotkeyHandler(
            hotkey=self._settings.hotkey,
            mode=self._settings.hotkey_mode,
            on_press=self._on_hotkey_press,
            on_release=self._on_hotkey_release,
        )
        self._tray = TrayIcon(
            on_settings=self._open_settings,
            on_quit=self._quit,
        )

    def run(self) -> None:
        """Startet die Anwendung (blockierend)."""
        self._hotkey.start()
        self._tray.run()  # Blockiert bis tray.stop() aufgerufen wird

    def _on_hotkey_press(self) -> None:
        with self._lock:
            if self._state != State.IDLE:
                return
            self._state = State.RECORDING
        self._tray.set_recording()
        try:
            self._recorder.start()
        except Exception as e:
            show_error(f"Mikrofon-Fehler: {e}")
            with self._lock:
                self._state = State.IDLE
            self._tray.set_idle()

    def _on_hotkey_release(self) -> None:
        with self._lock:
            if self._state != State.RECORDING:
                return
            self._state = State.PROCESSING
        self._tray.set_processing()
        threading.Thread(target=self._process, daemon=True).start()

    def _process(self) -> None:
        try:
            audio = self._recorder.stop()
            if len(audio) == 0:
                show_error("Keine Audiodaten aufgenommen.")
                return
            text = self._transcriber.transcribe(audio)
            if text:
                insert_text(text)
            else:
                show_error("Kein Text erkannt. Bitte erneut versuchen.")
        except Exception as e:
            show_error(f"Transkriptionsfehler: {e}")
        finally:
            with self._lock:
                self._state = State.IDLE
            self._tray.set_idle()

    def _open_settings(self) -> None:
        def on_save(new_settings: Settings) -> None:
            self._settings = new_settings
            self._hotkey.stop()
            self._recorder = AudioRecorder(device_index=new_settings.microphone_index)
            self._transcriber.reload(new_settings.model, new_settings.language)
            self._hotkey = HotkeyHandler(
                hotkey=new_settings.hotkey,
                mode=new_settings.hotkey_mode,
                on_press=self._on_hotkey_press,
                on_release=self._on_hotkey_release,
            )
            self._hotkey.start()

        threading.Thread(
            target=lambda: SettingsDialog(self._settings, on_save).show(),
            daemon=True,
        ).start()

    def _quit(self) -> None:
        self._hotkey.stop()
        self._tray.stop()
```

- [ ] **Step 2: Commit**

```bash
git add app.py
git commit -m "feat: app orchestrator with state machine (IDLE/RECORDING/PROCESSING)"
```

---

## Task 12: Einstiegspunkt (main.py)

**Files:**
- Create: `main.py`

- [ ] **Step 1: main.py implementieren**

```python
# main.py
import sys
from app import App


def main():
    app = App()
    app.run()


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Manuell Integrationstest**

```bash
python main.py
```

Prüfen:
1. Tray-Icon erscheint (grüner Kreis)
2. F12 halten → Icon wird rot
3. F12 loslassen → Icon wird gelb, dann grün
4. Text erscheint im aktiven Textfeld (z.B. Notepad)
5. Rechtsklick auf Icon → Menü zeigt "Einstellungen" und "Beenden"
6. Einstellungsdialog öffnet sich, Änderungen werden gespeichert

- [ ] **Step 3: Commit**

```bash
git add main.py
git commit -m "feat: entry point, app is fully functional"
```

---

## Task 13: Alle Tests ausführen & Aufräumen

- [ ] **Step 1: Vollständige Test-Suite ausführen**

```bash
pytest tests/ -v
```

Erwartete Ausgabe: Alle Tests `PASSED`.

- [ ] **Step 2: Anforderungen.md aktualisieren**

Geklärte Entscheidungen dokumentieren (Modell, Hotkey-Modus, etc.).

- [ ] **Step 3: Final Commit**

```bash
git add .
git commit -m "chore: final cleanup and full test run"
```

---

## Abhängigkeiten zwischen Tasks

```
Task 1 (Setup)
  └── Task 2 (Settings)
        ├── Task 5 (AudioRecorder)
        ├── Task 6 (Transcriber)
        ├── Task 9 (SettingsDialog) → braucht Task 5
        └── Task 11 (App) → braucht Tasks 3,4,5,6,7,8,9,10
  Task 3 (Icons) → Task 10 (TrayIcon)
  Task 4 (Notification)
  Task 7 (TextInserter)
  Task 8 (HotkeyHandler)
  Task 12 (main.py) → braucht Task 11
```

Tasks 3, 4, 7, 8 sind voneinander unabhängig und können parallel implementiert werden.
