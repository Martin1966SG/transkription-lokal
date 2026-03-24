# tests/test_text_inserter.py
import pytest
from unittest.mock import patch, call
from text_inserter import insert_text


def test_insert_text_saves_and_restores_clipboard():
    with patch("pyperclip.copy") as mock_copy, \
         patch("pyperclip.paste", return_value="original content"), \
         patch("text_inserter._simulate_paste") as mock_paste, \
         patch("time.sleep"):

        insert_text("transkribierter Text")

        assert call("transkribierter Text") in mock_copy.call_args_list
        mock_paste.assert_called_once()
        assert call("original content") in mock_copy.call_args_list


def test_insert_text_empty_string_does_nothing():
    with patch("pyperclip.copy") as mock_copy, \
         patch("pyperclip.paste", return_value="original"), \
         patch("text_inserter._simulate_paste") as mock_paste:

        insert_text("")
        mock_paste.assert_not_called()
