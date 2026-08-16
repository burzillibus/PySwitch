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
    from adafruit_midi.system_exclusive import SystemExclusive
    from lib.pyswitch.controller.client import Client, ClientParameterMapping
    from lib.pyswitch.clients.boss.gx100.actions import NAVI_PATCH_DOWN, NAVI_PATCH_UP, SHOW_RECEIVED_MEMORY, SYNC_GX100_MEMORY, SYNC_GX100_STOMPS
    from lib.pyswitch.clients.boss.gx100.mappings import (
        MAPPING_NAVI_MEMORY_CHANGE,
        MAPPING_RX_ASSIGN_CONTROL_CHANGE,
        MAPPING_RX_CURRENT_MEMORY,
        MAPPING_RX_FX_ITEM_STATE,
        MAPPING_RX_MEMORY_CHANGE,
        MAPPING_STOMP_CONTROL_CHANGE,
        MAPPING_TX_MEMORY_CHANGE,
    )
    from .mocks_appl import MockClientRequestListener, MockMidiController


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

    def test_publish_stomp_feedback_updates_its_listeners_without_sending_cc(self):
        client = Client(MockMidiController(), {})
        mapping = MAPPING_STOMP_CONTROL_CHANGE(64)
        listener = MockClientRequestListener()
        client.register(mapping, listener)

        client.publish_value(mapping, 127)

        self.assertEqual(mapping.value, 127)
        self.assertEqual(listener.parameter_changed_calls, [mapping])
        self.assertEqual(client.midi.messages_sent, [])

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

    def test_create_memory_send_mapping(self):
        mapping = MAPPING_TX_MEMORY_CHANGE()
        mapping.set_value(42)
        self.assertEqual(mapping.set.patch, 42)

    def test_read_current_memory_with_gx100_rq1(self):
        mapping = MAPPING_RX_CURRENT_MEMORY()
        self.assertEqual(mapping.request.manufacturer_id, [0x41])
        self.assertEqual(mapping.request.data[-5:], [0x00, 0x00, 0x00, 0x04, 0x7C])

        response = SystemExclusive(
            manufacturer_id = [0x41],
            data = [0x10, 0x00, 0x00, 0x00, 0x00, 0x0B, 0x12,
                    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x02, 0x0B, 0x00]
        )
        self.assertTrue(mapping.parse(response))
        self.assertEqual(mapping.value, 43)

    def test_read_fx_item_state_with_gx100_rq1(self):
        mapping = MAPPING_RX_FX_ITEM_STATE(3)
        self.assertEqual(mapping.request.data[-5:], [0x00, 0x00, 0x00, 0x01, 0x59])

        response = SystemExclusive(
            manufacturer_id = [0x41],
            data = [0x10, 0x00, 0x00, 0x00, 0x00, 0x0B, 0x12,
                    0x10, 0x00, 0x15, 0x01, 0x01, 0x59]
        )
        self.assertTrue(mapping.parse(response))
        self.assertEqual(mapping.value, 1)

    def test_reject_invalid_fx_item(self):
        with self.assertRaises(ValueError):
            MAPPING_RX_FX_ITEM_STATE(0)

        with self.assertRaises(ValueError):
            MAPPING_RX_FX_ITEM_STATE(21)

    def test_sync_action_requests_the_current_memory(self):
        client = type("Client", (), {"requests": [], "request": lambda self, mapping, listener: self.requests.append((mapping, listener))})()
        application = type("Application", (), {"client": client})()
        callback = SYNC_GX100_MEMORY().callback
        callback._appl = application

        callback.push()
        self.assertEqual(len(client.requests), 1)
        self.assertIs(callback._mapping, client.requests[0][0])

    def test_stomp_sync_queries_fx_items_after_memory_change(self):
        client = type("Client", (), {
            "requests": [],
            "published": [],
            "request": lambda self, mapping, listener: self.requests.append((mapping, listener)),
            "publish_value": lambda self, mapping, value: self.published.append((mapping, value)),
        })()
        application = type("Application", (), {"client": client})()
        callback = SYNC_GX100_STOMPS([64, 65]).callback
        callback._appl = application

        callback._memory_change.value = 8
        callback.parameter_changed(callback._memory_change)
        self.assertEqual([request[0] for request in client.requests], callback._states)

        callback._states[1].value = 1
        callback.parameter_changed(callback._states[1])
        self.assertIs(client.published[0][0], callback._stomps[1])
        self.assertEqual(client.published[0][1], 127)

    def test_patch_navigation_crosses_bank_boundaries(self):
        application = type("Application", (), {"client": type("Client", (), {
            "set_calls": [],
            "set": lambda self, mapping, value: self.set_calls.append((mapping, value)),
        })()})()

        patch_up = NAVI_PATCH_UP().callback
        patch_up._appl = application
        patch_up._memory.value = 3
        patch_up.push()

        patch_down = NAVI_PATCH_DOWN().callback
        patch_down._appl = application
        patch_down._memory.value = 4
        patch_down.push()

        self.assertEqual(application.client.set_calls[0][1], 4)
        self.assertEqual(application.client.set_calls[1][1], 3)

    def test_navigation_clamps_to_pc_1_through_pc_100(self):
        application = type("Application", (), {"client": type("Client", (), {
            "set_calls": [],
            "set": lambda self, mapping, value: self.set_calls.append((mapping, value)),
        })()})()
        callback = NAVI_PATCH_UP().callback
        callback._appl = application
        callback._memory.value = 99

        callback.push()
        self.assertEqual(application.client.set_calls[0][1], 99)

    def test_reject_invalid_navi_program_change_number(self):
        with self.assertRaises(ValueError):
            MAPPING_NAVI_MEMORY_CHANGE(-1)

        with self.assertRaises(ValueError):
            MAPPING_NAVI_MEMORY_CHANGE(128)
