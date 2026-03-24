# Anforderungen

Entwicklung einer lokalen Windows-Anwendung, die es ermöglicht, 
systemweit per Hotkey (F12) Sprache aufzunehmen, lokal zu 
transkribieren (Whisper) und den Text automatisch in
das aktuell aktive Textfeld einzufügen, unabhängig von der
verwendeten Anwendung.

- Hintergrunddienst ohne sichtbare UI
- Erzeugen eine Tray-Icons
- Das TrayIcon erhält ein Kontext-Menü zum Aufruf der Einstellungen
    - Einstellung des Mikrofon
    - Einstellung des HotKey
    Die Einstellungen zwischen den Aufrufen des Programms speichern
- Deutsche Sprache als Default
- Audioaufnahme Ober Standardmikrofon
- Verwendung der GPU, wenn nicht vorhanden dann cpu

# Tech Stack

I ----------------------------- I
| 1 | ** Python 3.10+ **        |
| 2 | ** faster-whisper"        |
| 3 | ** AutoHotkey (AHK) **    | 
| 4 | ** sounddevice"*          |
| 5 | ** pyperclip".            |
| 6 | ** CUDA / NVIDIA GPU **   |
