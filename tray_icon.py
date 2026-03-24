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
