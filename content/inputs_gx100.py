##############################################################################################################################################
# BOSS GX-100: Stomp/Navi layout.
#
# Stomp is the default. CC 64..73 are latched, colour-coded controls.
# Navi is entered by holding physical Key 3 and left by holding physical Key 6
# (the A switch). Navi LEDs mirror Program Changes received from the GX-100.
##############################################################################################################################################

from pyswitch.clients.boss.gx100.actions import SHOW_RECEIVED_MEMORY
from pyswitch.clients.boss.gx100.mappings import MAPPING_NAVI_MEMORY_CHANGE, MAPPING_STOMP_CONTROL_CHANGE
from pyswitch.clients.local.actions.binary_switch import BINARY_SWITCH
from pyswitch.clients.local.actions.mode import ModeSelector, SELECT_MODE
from pyswitch.colors import Colors
from pyswitch.controller.actions import PushButtonAction
from pyswitch.hardware.devices.pa_midicaptain_10 import *
from display import DISPLAY_HEADER_1, DISPLAY_HEADER_2, DISPLAY_FOOTER_1, DISPLAY_FOOTER_2, DISPLAY_RIG_NAME

_STOMP = "stomp"
_NAVI = "navi"
_MODE = ModeSelector(_STOMP, display = DISPLAY_RIG_NAME)


def _stomp(control, text, color, display = None):
    return BINARY_SWITCH(
        mapping = MAPPING_STOMP_CONTROL_CHANGE(control),
        text = text,
        color = color,
        display = display,
        mode = PushButtonAction.LATCH,
        value_on = 127,
        value_off = 0,
        use_internal_state = True,
        led_brightness_on = 0.30,
        led_brightness_off = 0.0,
        id = _STOMP,
        enable_callback = _MODE,
    )


def _memory(patch, display = None):
    return BINARY_SWITCH(
        mapping = MAPPING_NAVI_MEMORY_CHANGE(patch),
        text = "PC " + str(patch + 1),
        color = Colors.WHITE,
        display = display,
        mode = PushButtonAction.ONE_SHOT,
        value_on = patch,
        use_internal_state = False,
        led_brightness_on = 0.25,
        led_brightness_off = 0.0,
        comparison_mode = 0,  # BinaryParameterCallback.EQUAL
        reference_value = patch,
        id = _NAVI,
        enable_callback = _MODE,
    )


Inputs = [
    {"assignment": PA_MIDICAPTAIN_10_SWITCH_1, "actions": [_stomp(64, "FX 1", Colors.RED, DISPLAY_HEADER_1), _memory(0, DISPLAY_HEADER_1)]},
    {"assignment": PA_MIDICAPTAIN_10_SWITCH_2, "actions": [_stomp(65, "FX 2", Colors.GREEN, DISPLAY_HEADER_2), _memory(1, DISPLAY_HEADER_2)]},
    {
        "assignment": PA_MIDICAPTAIN_10_SWITCH_3,
        "actions": [_stomp(66, "FX 3", Colors.BLUE, DISPLAY_FOOTER_1), _memory(2, DISPLAY_FOOTER_1), SHOW_RECEIVED_MEMORY(display = DISPLAY_RIG_NAME)],
        "actionsHold": [SELECT_MODE(_MODE, _NAVI)],
    },
    {"assignment": PA_MIDICAPTAIN_10_SWITCH_4, "actions": [_stomp(67, "FX 4", Colors.ORANGE, DISPLAY_FOOTER_2), _memory(3, DISPLAY_FOOTER_2)]},
    {"assignment": PA_MIDICAPTAIN_10_SWITCH_UP, "actions": [_stomp(68, "FX 5", Colors.CYAN), _memory(4)]},
    {
        "assignment": PA_MIDICAPTAIN_10_SWITCH_A,
        "actions": [_stomp(69, "FX 6", Colors.PURPLE), _memory(5)],
        "actionsHold": [SELECT_MODE(_MODE, _STOMP)],
    },
    {"assignment": PA_MIDICAPTAIN_10_SWITCH_B, "actions": [_stomp(70, "FX 7", Colors.YELLOW), _memory(6)]},
    {"assignment": PA_MIDICAPTAIN_10_SWITCH_C, "actions": [_stomp(71, "FX 8", Colors.PINK), _memory(7)]},
    {"assignment": PA_MIDICAPTAIN_10_SWITCH_D, "actions": [_stomp(72, "FX 9", Colors.TURQUOISE), _memory(8)]},
    {"assignment": PA_MIDICAPTAIN_10_SWITCH_DOWN, "actions": [_stomp(73, "FX 10", Colors.LIGHT_GREEN), _memory(9)]},
]
