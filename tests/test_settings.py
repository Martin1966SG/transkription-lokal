# tests/test_settings.py
import os
import json
import tempfile
import pytest
from unittest.mock import patch
from settings import Settings, APPDATA_DIR

def test_default_values():
    s = Settings()
    assert s.hotkey == "f12"
    assert s.hotkey_mode == "hold"
    assert s.model == "small"
    assert s.language == "de"
    assert s.microphone_index is None

def test_save_and_load(tmp_path):
    config_path = tmp_path / "config.json"
    with patch("settings.CONFIG_PATH", str(config_path)):
        s = Settings(hotkey="f11", model="medium")
        s.save()
        loaded = Settings.load()
        assert loaded.hotkey == "f11"
        assert loaded.model == "medium"

def test_load_returns_defaults_when_no_file(tmp_path):
    config_path = tmp_path / "nonexistent.json"
    with patch("settings.CONFIG_PATH", str(config_path)):
        s = Settings.load()
        assert s.hotkey == "f12"

def test_load_merges_missing_keys(tmp_path):
    """Neue Felder in späteren Versionen haben defaults, auch wenn config-Datei alt ist."""
    config_path = tmp_path / "config.json"
    config_path.write_text(json.dumps({"hotkey": "f10"}))
    with patch("settings.CONFIG_PATH", str(config_path)):
        s = Settings.load()
        assert s.hotkey == "f10"
        assert s.model == "small"  # Default, weil nicht in alter config
