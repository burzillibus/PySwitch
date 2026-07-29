"""Mappings for messages transmitted by a BOSS GX-100.

The GX-100 sends a Program Change when a memory is selected (when MEMORY
MIDI is enabled), and can send Control Changes from its ASSIGN settings.
Use these mappings with a callback to react to messages received by PySwitch.
"""

from ....controller.client import ClientParameterMapping
from adafruit_midi.control_change import ControlChange
from adafruit_midi.program_change import ProgramChange


def MAPPING_RX_MEMORY_CHANGE():
    """Receive the Program Change transmitted for a GX-100 memory change."""
    return ClientParameterMapping.get(
        name = "BOSS GX-100 memory change",
        response = ProgramChange(0)
    )


def MAPPING_TX_MEMORY_CHANGE():
    """Select a GX-100 memory with a Program Change."""
    return ClientParameterMapping.get(
        name = "BOSS GX-100 memory select",
        set = ProgramChange(0)
    )


def MAPPING_RX_ASSIGN_CONTROL_CHANGE(control):
    """Receive a Control Change configured in one of the GX-100 ASSIGN slots."""
    if control < 0 or control > 127:
        raise ValueError("GX-100 Control Change number must be in range 0..127")

    return ClientParameterMapping.get(
        name = "BOSS GX-100 ASSIGN CC " + str(control),
        response = ControlChange(control, 0)
    )

def MAPPING_STOMP_CONTROL_CHANGE(control):
    """A latched GX-100 stomp control using a configured ASSIGN CC number."""
    if control < 64 or control > 95:
        raise ValueError("GX-100 stomp CC number must be in range 64..95")

    return ClientParameterMapping.get(
        name = "BOSS GX-100 stomp CC " + str(control),
        set = ControlChange(control, 0),
        response = ControlChange(control, 0)
    )

def MAPPING_NAVI_MEMORY_CHANGE(patch):
    """Select a GX-100 memory and use its Program Change as feedback."""
    if patch < 0 or patch > 127:
        raise ValueError("GX-100 Program Change number must be in range 0..127")

    return ClientParameterMapping.get(
        name = "BOSS GX-100 navi PC " + str(patch),
        set = ProgramChange(patch),
        response = ProgramChange(0)
    )
