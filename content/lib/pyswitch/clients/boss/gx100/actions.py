"""GX-100 UI actions."""

from ....controller.actions import Action
from ....controller.callbacks import Callback
from ....colors import Colors
from .mappings import MAPPING_RX_MEMORY_CHANGE


def SHOW_RECEIVED_MEMORY(display = None, color = Colors.LIGHT_GREEN):
    """Show the GX-100 memory selected through an incoming Program Change."""
    return Action({
        "callback": _ReceivedMemoryCallback(color),
        "display": display,
        "useSwitchLeds": False,
    })


class _ReceivedMemoryCallback(Callback):
    def __init__(self, color):
        self._mapping = MAPPING_RX_MEMORY_CHANGE()
        self._color = color
        super().__init__(mappings = [self._mapping])

    def push(self):
        pass

    def release(self):
        pass

    def update_displays(self):
        if not self.action.label:
            return

        if self._mapping.value is None:
            self.action.label.text = "GX-100 RX"
        else:
            # Program Change is zero based on the wire, users normally count 1..128.
            self.action.label.text = "GX PC " + str(self._mapping.value + 1)

        self.action.label.text_color = self._color
