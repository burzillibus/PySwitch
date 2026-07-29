import sys
import unittest
from unittest.mock import patch

from .mocks_lib import MockMicropython


class _Mapping:
    value = None
    response = None
    set = None


with patch.dict(sys.modules, {"micropython": MockMicropython}):
    from lib.pyswitch.controller.actions import PushButtonAction
    from lib.pyswitch.controller.callbacks import BinaryParameterCallback


class TestBinaryInternalState(unittest.TestCase):
    def test_internal_state_is_preserved_without_feedback(self):
        callback = BinaryParameterCallback(
            mapping = _Mapping(),
            use_internal_state = True
        )
        action = PushButtonAction({"callback": callback})
        action.feedback_state(True)

        callback.evaluate_value(None)

        self.assertTrue(action.state)

    def test_default_state_is_cleared_without_feedback(self):
        callback = BinaryParameterCallback(mapping = _Mapping())
        action = PushButtonAction({"callback": callback})
        action.feedback_state(True)

        callback.evaluate_value(None)

        self.assertFalse(action.state)
