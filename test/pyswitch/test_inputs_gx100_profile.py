import importlib.util
import sys
import unittest
from pathlib import Path
from types import ModuleType
from unittest.mock import patch


class _ModeSelector:
    def __init__(self, initial_mode, display = None, color = None):
        self.current_mode = initial_mode
        self.display = display
        self.color = color


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

    actions = ModuleType("pyswitch.clients.boss.gx100.actions")
    actions.SHOW_RECEIVED_MEMORY = lambda **kwargs: {"received_memory": kwargs}
    actions.NAVI_MODE_INDICATOR = lambda **kwargs: {"mode_indicator": kwargs}
    actions.NAVI_BANK_DOWN = lambda **kwargs: {"bank_down": kwargs}
    actions.NAVI_BANK_UP = lambda **kwargs: {"bank_up": kwargs}
    actions.NAVI_PATCH_DOWN = lambda **kwargs: {"patch_down": kwargs}
    actions.NAVI_PATCH_UP = lambda **kwargs: {"patch_up": kwargs}

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

    hardware = ModuleType("pyswitch.hardware.devices.pa_midicaptain_mini_6")
    keys = [object() for _ in range(6)]
    for name, key in zip([
        "PA_MIDICAPTAIN_MINI_SWITCH_1", "PA_MIDICAPTAIN_MINI_SWITCH_2",
        "PA_MIDICAPTAIN_MINI_SWITCH_3", "PA_MIDICAPTAIN_MINI_SWITCH_C",
        "PA_MIDICAPTAIN_MINI_SWITCH_B", "PA_MIDICAPTAIN_MINI_SWITCH_A",
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
        "pyswitch.hardware.devices.pa_midicaptain_mini_6": hardware,
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

    def test_stomp_is_default_and_the_five_stomp_controls_are_coloured_latches(self):
        self.assertEqual(self.profile._MODE.current_mode, "stomp")
        self.assertEqual(len(self.profile.Inputs), 6)

        expected_colours = [
            _Colors.RED, _Colors.GREEN, _Colors.BLUE, _Colors.ORANGE, _Colors.CYAN,
        ]
        for index, input_definition in enumerate(self.profile.Inputs[1:]):
            stomp = input_definition["actions"][0]
            self.assertEqual(stomp["mapping"], ("stomp", 64 + index))
            self.assertEqual(stomp["mode"], "latch")
            self.assertEqual(stomp["color"], expected_colours[index])
            self.assertEqual(stomp["led_brightness_on"], 0.30)
            self.assertEqual(stomp["led_brightness_off"], 0.0)
            self.assertEqual(stomp["id"], "stomp")

    def test_key_1_enters_navi_and_key_4_returns_to_stomp(self):
        key_1 = self.profile.Inputs[0]
        key_4 = self.profile.Inputs[3]

        self.assertEqual(key_1["assignment"], self.keys[0])
        self.assertEqual(key_1["actions"][0]["target"], "navi")
        self.assertEqual(key_4["assignment"], self.keys[5])
        self.assertEqual(key_4["actions"][1]["target"], "stomp")

        key_6 = self.profile.Inputs[5]
        self.assertEqual(key_6["assignment"], self.keys[3])
        self.assertIn("patch_up", key_6["actions"][1])

    def test_mode_text_is_red_in_stomp_and_navi(self):
        self.assertEqual(self.profile._MODE.color, _Colors.RED)

    def test_navi_controls_use_the_requested_navigation_and_led_colours(self):
        actions = [input_definition["actions"] for input_definition in self.profile.Inputs]

        self.assertEqual(actions[0][1]["mode_indicator"]["id"], "navi")
        self.assertEqual(actions[0][1]["mode_indicator"]["color"], _Colors.WHITE)
        self.assertEqual(actions[1][1]["bank_down"]["id"], "navi")
        self.assertEqual(actions[2][1]["bank_up"]["id"], "navi")
        self.assertEqual(actions[3][2]["mode_indicator"]["color"], _Colors.WHITE)
        self.assertEqual(actions[4][1]["patch_down"]["id"], "navi")
        self.assertEqual(actions[5][1]["patch_up"]["id"], "navi")
        self.assertEqual(actions[2][2]["received_memory"]["color"], _Colors.RED)
