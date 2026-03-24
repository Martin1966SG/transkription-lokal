# notification.py
import tkinter as tk
import threading
from queue import Empty, SimpleQueue


_STATUS_COLORS = {
    "recording":  ("#b71c1c", "white", "🔴 Aufnahme läuft..."),
    "processing": ("#e65100", "white", "🟡 Transkription läuft..."),
    "idle":       ("#1b5e20", "white", "🟢 Bereit"),
    "error":      ("#c62828", "white", None),
}

_ui_lock = threading.Lock()
_ui_started = False
_cmd_queue = SimpleQueue()


def _ensure_ui_thread() -> None:
    global _ui_started
    with _ui_lock:
        if _ui_started:
            return
        threading.Thread(target=_ui_loop, daemon=True).start()
        _ui_started = True


def show_error(message: str, duration_ms: int = 4000) -> None:
    """Zeigt ein rotes Fehler-Popup unten rechts an."""
    _ensure_ui_thread()
    bg, fg, _ = _STATUS_COLORS["error"]
    _cmd_queue.put(("show_error", {"message": message, "duration_ms": duration_ms, "bg": bg, "fg": fg}))


def show_status(state: str, duration_ms: int = 2000) -> None:
    """Zeigt ein farbiges Status-Popup unten rechts an.
    state: 'recording' | 'processing' | 'idle'
    """
    if state not in _STATUS_COLORS:
        return
    _ensure_ui_thread()
    bg, fg, default_msg = _STATUS_COLORS[state]
    if default_msg is None:
        return
    # Aufnahme- und Verarbeitungsstatus bleiben sichtbar, bis ein neuer Status gesetzt wird.
    effective_duration = 0 if state in ("recording", "processing") else duration_ms
    _cmd_queue.put(
        (
            "show_status",
            {
                "message": default_msg,
                "duration_ms": effective_duration,
                "bg": bg,
                "fg": fg,
            },
        )
    )


def hide_status() -> None:
    """Schließt ein aktives Status-Popup (falls vorhanden)."""
    if not _ui_started:
        return
    _cmd_queue.put(("hide_status", {}))


def _ui_loop() -> None:
    root = tk.Tk()
    root.withdraw()
    active_status_window: tk.Toplevel | None = None

    def _close_status() -> None:
        nonlocal active_status_window
        if active_status_window is not None and active_status_window.winfo_exists():
            active_status_window.destroy()
        active_status_window = None

    def _show_popup(message: str, bg: str, fg: str, duration_ms: int, is_status: bool) -> tk.Toplevel:
        nonlocal active_status_window
        if is_status:
            _close_status()

        win = tk.Toplevel(root)
        win.overrideredirect(True)
        win.attributes("-topmost", True)
        win.configure(bg=bg)

        label = tk.Label(
            win,
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

        win.update_idletasks()
        w = win.winfo_width()
        h = win.winfo_height()
        screen_w = win.winfo_screenwidth()
        screen_h = win.winfo_screenheight()
        x = screen_w - w - 16
        y = screen_h - h - 64
        win.geometry(f"+{x}+{y}")

        if duration_ms > 0:
            win.after(duration_ms, win.destroy)

        if is_status:
            active_status_window = win
            win.bind("<Destroy>", lambda _e: _close_status())

        return win

    def _drain_commands() -> None:
        while True:
            try:
                action, payload = _cmd_queue.get_nowait()
            except Empty:
                break

            if action == "show_status":
                _show_popup(
                    message=payload["message"],
                    bg=payload["bg"],
                    fg=payload["fg"],
                    duration_ms=payload["duration_ms"],
                    is_status=True,
                )
            elif action == "show_error":
                _close_status()
                _show_popup(
                    message=payload["message"],
                    bg=payload["bg"],
                    fg=payload["fg"],
                    duration_ms=payload["duration_ms"],
                    is_status=False,
                )
            elif action == "hide_status":
                _close_status()

        root.after(50, _drain_commands)

    root.after(50, _drain_commands)
    root.mainloop()
