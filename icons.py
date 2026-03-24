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
