##############################################################################################################################################
# BOSS GX-100 over the MIDI Captain DIN ports.
# The GX-100 defaults to MIDI channel 1, represented by channel number 0 here.
##############################################################################################################################################

from pyswitch.controller.midi import MidiRouting
from pyswitch.hardware.devices.pa_midicaptain import PA_MIDICAPTAIN_DIN_MIDI

_DIN_MIDI = PA_MIDICAPTAIN_DIN_MIDI(
    in_channel = None,
    out_channel = 0
)

Communication = {
    "midi": {
        "routings": [
            MidiRouting(source = _DIN_MIDI, target = MidiRouting.APPLICATION),
            MidiRouting(source = MidiRouting.APPLICATION, target = _DIN_MIDI),
        ]
    }
}
