import sys
import unittest
from unittest.mock import patch

from .mocks_lib import *


with patch.dict(sys.modules, {
    "micropython": MockMicropython,
    "adafruit_midi": MockAdafruitMIDI(),
    "adafruit_midi.control_change": MockAdafruitMIDIControlChange(),
    "adafruit_midi.program_change": MockAdafruitMIDIProgramChange(),
    "adafruit_midi.system_exclusive": MockAdafruitMIDISystemExclusive(),
}):
    from adafruit_midi.control_change import ControlChange
    from adafruit_midi.program_change import ProgramChange
    from lib.pyswitch.controller.client import ClientParameterMapping
    from lib.pyswitch.clients.boss.gx100.actions import SHOW_RECEIVED_MEMORY
    from lib.pyswitch.clients.boss.gx100.mappings import (
        MAPPING_NAVI_MEMORY_CHANGE,
        MAPPING_RX_ASSIGN_CONTROL_CHANGE,
        MAPPING_RX_MEMORY_CHANGE,
        MAPPING_STOMP_CONTROL_CHANGE,
    )


class TestBossGx100Mappings(unittest.TestCase):

    def setUp(self):
        ClientParameterMapping._mappings = []

    def test_receive_memory_change(self):
        mapping = MAPPING_RX_MEMORY_CHANGE()

        self.assertTrue(mapping.parse(ProgramChange(42)))
        self.assertEqual(mapping.value, 42)

    def test_receive_assign_control_change(self):
        mapping = MAPPING_RX_ASSIGN_CONTROL_CHANGE(12)

        self.assertFalse(mapping.parse(ControlChange(11, 127)))
        self.assertTrue(mapping.parse(ControlChange(12, 87)))
        self.assertEqual(mapping.value, 87)

    def test_reject_invalid_control_change_number(self):
        with self.assertRaises(ValueError):
            MAPPING_RX_ASSIGN_CONTROL_CHANGE(-1)

        with self.assertRaises(ValueError):
            MAPPING_RX_ASSIGN_CONTROL_CHANGE(128)
    def test_create_memory_receive_action(self):
        action = SHOW_RECEIVED_MEMORY()
        self.assertIsNotNone(action.callback)
    def test_create_stomp_mapping(self):
        mapping = MAPPING_STOMP_CONTROL_CHANGE(64)
        self.assertEqual(mapping.set.control, 64)
        self.assertEqual(mapping.response.control, 64)

    def test_reject_invalid_stomp_control_change_number(self):
        with self.assertRaises(ValueError):
            MAPPING_STOMP_CONTROL_CHANGE(63)

        with self.assertRaises(ValueError):
            MAPPING_STOMP_CONTROL_CHANGE(96)
    def test_create_navi_memory_mapping(self):
        mapping = MAPPING_NAVI_MEMORY_CHANGE(5)
        self.assertEqual(mapping.set.patch, 5)
        self.assertTrue(mapping.parse(ProgramChange(5)))
        self.assertEqual(mapping.value, 5)

    def test_reject_invalid_navi_program_change_number(self):
        with self.assertRaises(ValueError):
            MAPPING_NAVI_MEMORY_CHANGE(-1)

        with self.assertRaises(ValueError):
            MAPPING_NAVI_MEMORY_CHANGE(128)

