# notification.py
import tkinter as tk
import threading


_STATUS_COLORS = {
    "recording":  ("#b71c1c", "white", "🔴 Aufnahme läuft..."),
    "processing": ("#e65100", "white", "🟡 Transkription läuft..."),
    "idle":       ("#1b5e20", "white", "🟢 Bereit"),
    "error":      ("#c62828", "white", None),
}


def show_error(message: str, duration_ms: int = 4000) -> None:
    """Zeigt ein rotes Fehler-Popup unten rechts an."""
    bg, fg, _ = _STATUS_COLORS["error"]
    t = threading.Thread(target=_show, args=(message, duration_ms, bg, fg), daemon=True)
    t.start()


def show_status(state: str, duration_ms: int = 2000) -> None:
    """Zeigt ein farbiges Status-Popup unten rechts an.
    state: 'recording' | 'processing' | 'idle'
    """
    if state not in _STATUS_COLORS:
        return
    bg, fg, default_msg = _STATUS_COLORS[state]
    if default_msg is None:
        return
    t = threading.Thread(target=_show, args=(default_msg, duration_ms, bg, fg), daemon=True)
    t.start()


def _show(message: str, duration_ms: int, bg: str, fg: str) -> None:
    root = tk.Tk()
    root.overrideredirect(True)       # Kein Fensterrahmen
    root.attributes("-topmost", True) # Immer im Vordergrund
    root.configure(bg=bg)

    label = tk.Label(
        root,
        text=message,
        bg=bg,
        fg=fg,
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
