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
