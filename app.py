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
from notification import show_error, show_status, hide_status


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
        show_status("recording")
        try:
            self._recorder.start()
        except Exception as e:
            hide_status()
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
        show_status("processing")
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
            show_status("idle", duration_ms=1500)

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
        hide_status()
        self._hotkey.stop()
        self._tray.stop()
