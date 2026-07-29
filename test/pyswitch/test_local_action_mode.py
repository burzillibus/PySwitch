import sys
import unittest
from unittest.mock import patch

from .mocks_lib import MockMicropython

with patch.dict(sys.modules, {"micropython": MockMicropython}):
    from lib.pyswitch.clients.local.actions.mode import ModeSelector, SELECT_MODE


class _Display:
    text = None


class _Action:
    def __init__(self, identifier):
        self.id = identifier
        self.update_calls = 0

    def update(self):
        self.update_calls += 1


class _Input:
    def __init__(self, actions):
        self.actions = actions


class _Application:
    def __init__(self, actions):
        self.inputs = [_Input(actions)]


class TestModeSelector(unittest.TestCase):
    def test_select_mode_refreshes_actions_and_updates_display(self):
        display = _Display()
        stomp = _Action("stomp")
        navi = _Action("navi")
        selector = ModeSelector("stomp", display)
        application = _Application([stomp, navi])

        selector.init(application)
        self.assertEqual(display.text, "STOMP")
        self.assertTrue(selector.enabled(stomp))
        self.assertFalse(selector.enabled(navi))

        selector.select("navi")
        self.assertEqual(display.text, "NAVI")
        self.assertFalse(selector.enabled(stomp))
        self.assertTrue(selector.enabled(navi))
        self.assertEqual(stomp.update_calls, 1)
        self.assertEqual(navi.update_calls, 1)

    def test_select_mode_action_uses_same_selector(self):
        selector = ModeSelector("stomp")
        action = SELECT_MODE(selector, "navi")
        application = _Application([])

        action.init(application, None)
        action.push()

        self.assertEqual(selector.current_mode, "navi")
