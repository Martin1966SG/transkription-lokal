# hotkey_handler.py
import threading
from typing import Callable, Optional
from pynput import keyboard
from pynput.keyboard import Key, KeyCode


def _parse_key(hotkey_str: str):
    """Konvertiert z.B. 'f12' -> pynput Key.f12 oder KeyCode."""
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
