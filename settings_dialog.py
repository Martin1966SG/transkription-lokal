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
