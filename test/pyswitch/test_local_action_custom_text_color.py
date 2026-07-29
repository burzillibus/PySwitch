import sys
import unittest
from unittest.mock import patch

from .mocks_lib import *

with patch.dict(sys.modules, {
    "micropython": MockMicropython,
    "displayio": MockDisplayIO(),
    "adafruit_display_text": MockAdafruitDisplayText(),
    "adafruit_display_shapes.rect": MockDisplayShapes().rect(),
    "adafruit_midi.midi_message": MockAdafruitMIDIMessage(),
}):
    from lib.pyswitch.clients.local.actions.custom import CUSTOM_MESSAGE


class _Label:
    def __init__(self):
        self.text = ""
        self.text_color = None
        self.back_color = (1, 2, 3)


class _Switch:
    def __init__(self, action):
        self.pixels = []
        self.actions = [action]
        self.colors = []
        self.brightnesses = []


class _Midi:
    def send(self, message):
        pass


class _Application:
    class _Client:
        midi = _Midi()
    client = _Client()


class TestCustomMessageTextColor(unittest.TestCase):
    def test_text_color_only_avoids_background_changes(self):
        label = _Label()
        action = CUSTOM_MESSAGE(
            message = [1, 2],
            color = (8, 9, 2),
            text = "GX",
            display = label,
            text_color_only = True,
            use_leds = False
        )

        action.init(_Application(), _Switch(action))
        action.update_displays()

        self.assertEqual(label.text, "GX")
        self.assertEqual(label.text_color, (8, 9, 2))
        self.assertEqual(label.back_color, (1, 2, 3))
