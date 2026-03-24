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
