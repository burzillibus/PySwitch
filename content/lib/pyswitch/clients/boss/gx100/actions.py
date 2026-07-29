"""GX-100 UI actions."""

from ....controller.actions import Action
from ....controller.callbacks import Callback
from ....colors import Colors
from .mappings import MAPPING_RX_MEMORY_CHANGE, MAPPING_TX_MEMORY_CHANGE


_MEMORIES_PER_BANK = 4


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


def NAVI_BANK_DOWN(display = None, id = None, enable_callback = None):
    """Select the same patch in the preceding GX-100 bank."""
    return _navi_memory_change(-_MEMORIES_PER_BANK, "Bank -", Colors.RED, display, id, enable_callback)


def NAVI_BANK_UP(display = None, id = None, enable_callback = None):
    """Select the same patch in the following GX-100 bank."""
    return _navi_memory_change(_MEMORIES_PER_BANK, "Bank +", Colors.GREEN, display, id, enable_callback)


def NAVI_PATCH_DOWN(display = None, id = None, enable_callback = None):
    """Select the preceding patch, wrapping within the current GX-100 bank."""
    return _navi_memory_change(-1, "Patch -", Colors.RED, display, id, enable_callback, wrap_patch = True)


def NAVI_PATCH_UP(display = None, id = None, enable_callback = None):
    """Select the following patch, wrapping within the current GX-100 bank."""
    return _navi_memory_change(1, "Patch +", Colors.GREEN, display, id, enable_callback, wrap_patch = True)


def NAVI_MODE_INDICATOR(color = Colors.WHITE, id = None, enable_callback = None):
    """An always-lit navigation mode control without sending MIDI."""
    return Action({
        "callback": _NaviIndicatorCallback(color),
        "id": id,
        "useSwitchLeds": True,
        "enableCallback": enable_callback,
    })


def _navi_memory_change(delta, text, color, display, id, enable_callback, wrap_patch = False):
    return Action({
        "callback": _NaviMemoryChangeCallback(delta, text, color, wrap_patch),
        "display": display,
        "id": id,
        "useSwitchLeds": True,
        "enableCallback": enable_callback,
    })


class _NaviMemoryChangeCallback(Callback):
    def __init__(self, delta, text, color, wrap_patch):
        self._memory = MAPPING_RX_MEMORY_CHANGE()
        self._memory_select = MAPPING_TX_MEMORY_CHANGE()
        self._delta = delta
        self._text = text
        self._color = color
        self._wrap_patch = wrap_patch
        super().__init__(mappings = [self._memory])

    def init(self, appl, listener = None):
        super().init(appl, listener)
        self._appl = appl

    def push(self):
        current = self._memory.value
        if current is None:
            return

        if self._wrap_patch:
            bank_start = current - (current % _MEMORIES_PER_BANK)
            target = bank_start + ((current + self._delta) % _MEMORIES_PER_BANK)
        else:
            target = current + self._delta

        if target < 0:
            target = 0
        elif target > 127:
            target = 127

        self._appl.client.set(self._memory_select, target)

    def release(self):
        pass

    def update_displays(self):
        self.action.switch_color = self._color
        self.action.switch_brightness = 0.30
        if self.action.label:
            self.action.label.text = self._text
            self.action.label.text_color = self._color


class _NaviIndicatorCallback(Callback):
    def __init__(self, color):
        self._color = color
        super().__init__()

    def push(self):
        pass

    def release(self):
        pass

    def update_displays(self):
        self.action.switch_color = self._color
        self.action.switch_brightness = 0.30
