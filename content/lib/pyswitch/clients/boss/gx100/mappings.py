"""Mappings for messages transmitted by a BOSS GX-100.

The GX-100 sends a Program Change when a memory is selected (when MEMORY
MIDI is enabled), and can send Control Changes from its ASSIGN settings.
Use these mappings with a callback to react to messages received by PySwitch.
"""

from ....controller.client import ClientParameterMapping
from adafruit_midi.control_change import ControlChange
from adafruit_midi.program_change import ProgramChange
from adafruit_midi.system_exclusive import SystemExclusive


_GX100_DEVICE_ID = 0x10
_GX100_MODEL_ID = [0x00, 0x00, 0x00, 0x00, 0x0B]
_GX100_RQ1 = 0x11
_GX100_DT1 = 0x12
_CURRENT_MEMORY_ADDRESS = [0x00, 0x00, 0x00, 0x00]


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


def MAPPING_RX_CURRENT_MEMORY():
    """Read the GX-100's current memory number through its RQ1 SysEx command."""
    name = "BOSS GX-100 current memory"
    for mapping in ClientParameterMapping._mappings:
        if mapping.name == name:
            return mapping

    mapping = _CurrentMemoryMapping(name)
    ClientParameterMapping._mappings.append(mapping)
    return mapping


class _CurrentMemoryMapping(ClientParameterMapping):
    def __init__(self, name):
        # RQ1: address 00 00 00 00, size 00 00 00 04. The checksum is 7C.
        request = _roland_rq1(_CURRENT_MEMORY_ADDRESS, [0x00, 0x00, 0x00, 0x04])
        response = _roland_dt1_template(_CURRENT_MEMORY_ADDRESS)
        super().__init__(
            name = name,
            create_key = ClientParameterMapping,
            request = request,
            response = response,
        )

    def parse(self, midi_message):
        data = _roland_dt1_data(midi_message, _CURRENT_MEMORY_ADDRESS)
        if not data or len(data) < 4:
            return False

        digits = data[:4]
        for digit in digits:
            if digit > 0x0F:
                return False

        # The GX-100 stores the current memory number as four 4-bit digits.
        self.value = (digits[0] << 12) + (digits[1] << 8) + (digits[2] << 4) + digits[3]
        return True


def _roland_rq1(address, size):
    checksum = (-(sum(address) + sum(size))) % 0x80
    return SystemExclusive(
        manufacturer_id = [0x41],
        data = [_GX100_DEVICE_ID] + _GX100_MODEL_ID + [_GX100_RQ1] + address + size + [checksum]
    )


def _roland_dt1_template(address):
    return SystemExclusive(
        manufacturer_id = [0x41],
        data = [_GX100_DEVICE_ID] + _GX100_MODEL_ID + [_GX100_DT1] + address
    )


def _roland_dt1_data(midi_message, address):
    if not isinstance(midi_message, SystemExclusive):
        return None
    if len(midi_message.manufacturer_id) != 1 or midi_message.manufacturer_id[0] != 0x41:
        return None

    data = midi_message.data
    header = [_GX100_DEVICE_ID] + _GX100_MODEL_ID + [_GX100_DT1]
    if len(data) < 12:
        return None
    for index in range(7):
        if data[index] != header[index]:
            return None
    for index in range(4):
        if data[7 + index] != address[index]:
            return None

    # Exclude the Roland checksum at the end.
    return data[11:-1]


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
