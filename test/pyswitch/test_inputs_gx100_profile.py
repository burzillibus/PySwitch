import importlib.util
import sys
import unittest
from pathlib import Path
from types import ModuleType
from unittest.mock import patch


class _ModeSelector:
    def __init__(self, initial_mode, display = None):
        self.current_mode = initial_mode
        self.display = display


class _Colors:
    RED = "red"
    GREEN = "green"
    BLUE = "blue"
    ORANGE = "orange"
    CYAN = "cyan"
    PURPLE = "purple"
    YELLOW = "yellow"
    PINK = "pink"
    TURQUOISE = "turquoise"
    LIGHT_GREEN = "light_green"
    WHITE = "white"


def _load_profile():
    mappings = ModuleType("pyswitch.clients.boss.gx100.mappings")
    mappings.MAPPING_STOMP_CONTROL_CHANGE = lambda control: ("stomp", control)
    mappings.MAPPING_NAVI_MEMORY_CHANGE = lambda patch: ("navi", patch)

    actions = ModuleType("pyswitch.clients.boss.gx100.actions")
    actions.SHOW_RECEIVED_MEMORY = lambda **kwargs: {"received_memory": kwargs}

    binary = ModuleType("pyswitch.clients.local.actions.binary_switch")
    binary.BINARY_SWITCH = lambda **kwargs: kwargs

    mode = ModuleType("pyswitch.clients.local.actions.mode")
    mode.ModeSelector = _ModeSelector
    mode.SELECT_MODE = lambda selector, target: {"selector": selector, "target": target}

    colors = ModuleType("pyswitch.colors")
    colors.Colors = _Colors

    controller_actions = ModuleType("pyswitch.controller.actions")
    controller_actions.PushButtonAction = type("PushButtonAction", (), {
        "LATCH": "latch",
        "ONE_SHOT": "one_shot",
    })

    hardware = ModuleType("pyswitch.hardware.devices.pa_midicaptain_10")
    keys = [object() for _ in range(10)]
    for name, key in zip([
        "PA_MIDICAPTAIN_10_SWITCH_1", "PA_MIDICAPTAIN_10_SWITCH_2",
        "PA_MIDICAPTAIN_10_SWITCH_3", "PA_MIDICAPTAIN_10_SWITCH_4",
        "PA_MIDICAPTAIN_10_SWITCH_UP", "PA_MIDICAPTAIN_10_SWITCH_A",
        "PA_MIDICAPTAIN_10_SWITCH_B", "PA_MIDICAPTAIN_10_SWITCH_C",
        "PA_MIDICAPTAIN_10_SWITCH_D", "PA_MIDICAPTAIN_10_SWITCH_DOWN",
    ], keys):
        setattr(hardware, name, key)

    display = ModuleType("display")
    for name in [
        "DISPLAY_HEADER_1", "DISPLAY_HEADER_2", "DISPLAY_FOOTER_1",
        "DISPLAY_FOOTER_2", "DISPLAY_RIG_NAME",
    ]:
        setattr(display, name, name)

    modules = {
        "pyswitch.clients.boss.gx100.mappings": mappings,
        "pyswitch.clients.boss.gx100.actions": actions,
        "pyswitch.clients.local.actions.binary_switch": binary,
        "pyswitch.clients.local.actions.mode": mode,
        "pyswitch.colors": colors,
        "pyswitch.controller.actions": controller_actions,
        "pyswitch.hardware.devices.pa_midicaptain_10": hardware,
        "display": display,
    }
    source = Path(__file__).parents[2] / "content" / "inputs_gx100.py"
    spec = importlib.util.spec_from_file_location("inputs_gx100_profile_test", source)
    module = importlib.util.module_from_spec(spec)
    with patch.dict(sys.modules, modules):
        spec.loader.exec_module(module)
    return module, keys


class TestGx100InputsProfile(unittest.TestCase):
    def setUp(self):
        self.profile, self.keys = _load_profile()

    def test_stomp_is_default_and_all_ten_controls_are_coloured_latches(self):
        self.assertEqual(self.profile._MODE.current_mode, "stomp")
        self.assertEqual(len(self.profile.Inputs), 10)

        expected_colours = [
            _Colors.RED, _Colors.GREEN, _Colors.BLUE, _Colors.ORANGE, _Colors.CYAN,
            _Colors.PURPLE, _Colors.YELLOW, _Colors.PINK, _Colors.TURQUOISE, _Colors.LIGHT_GREEN,
        ]
        for index, input_definition in enumerate(self.profile.Inputs):
            stomp = input_definition["actions"][0]
            self.assertEqual(stomp["mapping"], ("stomp", 64 + index))
            self.assertEqual(stomp["mode"], "latch")
            self.assertEqual(stomp["color"], expected_colours[index])
            self.assertEqual(stomp["led_brightness_on"], 0.30)
            self.assertEqual(stomp["led_brightness_off"], 0.0)
            self.assertEqual(stomp["id"], "stomp")

    def test_key_3_enters_navi_and_key_6_returns_to_stomp(self):
        key_3 = self.profile.Inputs[2]
        key_6 = self.profile.Inputs[5]

        self.assertEqual(key_3["assignment"], self.keys[2])
        self.assertEqual(key_3["actionsHold"][0]["target"], "navi")
        self.assertEqual(key_6["assignment"], self.keys[5])
        self.assertEqual(key_6["actionsHold"][0]["target"], "stomp")

    def test_navi_actions_use_program_change_feedback_for_sync(self):
        for index, input_definition in enumerate(self.profile.Inputs):
            navi = input_definition["actions"][1]
            self.assertEqual(navi["mapping"], ("navi", index))
            self.assertEqual(navi["mode"], "one_shot")
            self.assertEqual(navi["reference_value"], index)
            self.assertEqual(navi["id"], "navi")
            self.assertFalse(navi["use_internal_state"])
            self.assertEqual(navi["led_brightness_off"], 0.0)
