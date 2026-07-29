##############################################################################################################################################
# BOSS GX-100: MIDI Captain Mini6 Stomp/Navi layout.
#
# Stomp is the default. Key 1 enters Navi; in Navi, keys 2/3 select the
# previous/next bank and keys 5/6 select the previous/next patch. Key 4
# returns to Stomp. Navigation follows Program Changes received from the GX-100.
##############################################################################################################################################

from pyswitch.clients.boss.gx100.actions import (
    NAVI_BANK_DOWN, NAVI_BANK_UP, NAVI_MODE_INDICATOR, NAVI_PATCH_DOWN,
    NAVI_PATCH_UP, SHOW_RECEIVED_MEMORY,
)
from pyswitch.clients.boss.gx100.mappings import MAPPING_STOMP_CONTROL_CHANGE
from pyswitch.clients.local.actions.binary_switch import BINARY_SWITCH
from pyswitch.clients.local.actions.mode import ModeSelector, SELECT_MODE
from pyswitch.colors import Colors
from pyswitch.controller.actions import PushButtonAction
from pyswitch.hardware.devices.pa_midicaptain_mini_6 import *
from display import DISPLAY_HEADER_1, DISPLAY_HEADER_2, DISPLAY_FOOTER_1, DISPLAY_FOOTER_2, DISPLAY_RIG_NAME

_STOMP = "stomp"
_NAVI = "navi"
_MODE = ModeSelector(_STOMP, display = DISPLAY_RIG_NAME, color = Colors.RED)


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


Inputs = [
    {
        "assignment": PA_MIDICAPTAIN_MINI_SWITCH_1,
        "actions": [
            SELECT_MODE(_MODE, _NAVI),
            NAVI_MODE_INDICATOR(color = Colors.WHITE, id = _NAVI, enable_callback = _MODE),
        ],
    },
    {
        "assignment": PA_MIDICAPTAIN_MINI_SWITCH_2,
        "actions": [
            _stomp(64, "FX 1", Colors.RED, DISPLAY_HEADER_1),
            NAVI_BANK_DOWN(display = DISPLAY_HEADER_1, id = _NAVI, enable_callback = _MODE),
        ],
    },
    {
        "assignment": PA_MIDICAPTAIN_MINI_SWITCH_3,
        "actions": [
            _stomp(65, "FX 2", Colors.GREEN, DISPLAY_HEADER_2),
            NAVI_BANK_UP(display = DISPLAY_HEADER_2, id = _NAVI, enable_callback = _MODE),
            SHOW_RECEIVED_MEMORY(display = DISPLAY_RIG_NAME, color = Colors.RED),
        ],
    },
    {
        "assignment": PA_MIDICAPTAIN_MINI_SWITCH_A,
        "actions": [
            _stomp(66, "FX 3", Colors.BLUE, DISPLAY_FOOTER_1),
            SELECT_MODE(_MODE, _STOMP),
            NAVI_MODE_INDICATOR(color = Colors.WHITE, id = _NAVI, enable_callback = _MODE),
        ],
    },
    {
        "assignment": PA_MIDICAPTAIN_MINI_SWITCH_B,
        "actions": [
            _stomp(67, "FX 4", Colors.ORANGE, DISPLAY_FOOTER_2),
            NAVI_PATCH_DOWN(display = DISPLAY_FOOTER_1, id = _NAVI, enable_callback = _MODE),
        ],
    },
    {
        "assignment": PA_MIDICAPTAIN_MINI_SWITCH_C,
        "actions": [
            _stomp(68, "FX 5", Colors.CYAN),
            NAVI_PATCH_UP(display = DISPLAY_FOOTER_2, id = _NAVI, enable_callback = _MODE),
        ],
    },
]
