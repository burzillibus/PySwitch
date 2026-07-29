"""GX-100 UI actions."""

from ....controller.actions import Action
from ....controller.callbacks import Callback
from ....colors import Colors
from .mappings import (
    MAPPING_RX_CURRENT_MEMORY, MAPPING_RX_MEMORY_CHANGE, MAPPING_TX_MEMORY_CHANGE,
)


_MEMORIES_PER_BANK = 4
_MAX_MEMORY = 99  # PC#1..PC#100 map directly to U01-1..U25-4 in FIX mode.


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


def SYNC_GX100_MEMORY(display = None, color = Colors.RED):
    """Request the GX-100 current memory when entering navigation mode."""
    return Action({
        "callback": _SyncMemoryCallback(color),
        "display": display,
        "useSwitchLeds": False,
    })


class _SyncMemoryCallback(Callback):
    def __init__(self, color):
        self._mapping = MAPPING_RX_CURRENT_MEMORY()
        self._memory_feedback = MAPPING_RX_MEMORY_CHANGE()
        self._color = color
        super().__init__(mappings = [self._mapping])

    def init(self, appl, listener = None):
        super().init(appl, listener)
        self._appl = appl

    def update(self):
        # Sync only when NAVI is entered; do not repeatedly poll the GX-100.
        pass

    def push(self):
        self._appl.client.request(self._mapping, self)

    def release(self):
        pass

    def update_displays(self):
        memory = self._mapping.value

        if memory is not None and memory <= _MAX_MEMORY:
            # In MAP SELECT = FIX, zero-based memory and PC values match.
            self._memory_feedback.value = memory

        if not self.action.label:
            return
        if memory is None:
            self.action.label.text = "GX-100 SYNC"
        elif memory <= _MAX_MEMORY:
            self.action.label.text = "GX PC " + str(memory + 1)
        else:
            self.action.label.text = "GX MEM " + str(memory + 1)
        self.action.label.text_color = self._color


def NAVI_BANK_DOWN(display = None, id = None, enable_callback = None):
    """Select the same patch in the preceding GX-100 bank."""
    return _navi_memory_change(-_MEMORIES_PER_BANK, "Bank -", Colors.RED, display, id, enable_callback)


def NAVI_BANK_UP(display = None, id = None, enable_callback = None):
    """Select the same patch in the following GX-100 bank."""
    return _navi_memory_change(_MEMORIES_PER_BANK, "Bank +", Colors.GREEN, display, id, enable_callback)


def NAVI_PATCH_DOWN(display = None, id = None, enable_callback = None):
    """Select the preceding patch, crossing into the preceding bank when needed."""
    return _navi_memory_change(-1, "Patch -", Colors.RED, display, id, enable_callback)


def NAVI_PATCH_UP(display = None, id = None, enable_callback = None):
    """Select the following patch, crossing into the following bank when needed."""
    return _navi_memory_change(1, "Patch +", Colors.GREEN, display, id, enable_callback)


def NAVI_MODE_INDICATOR(color = Colors.WHITE, id = None, enable_callback = None):
    """An always-lit navigation mode control without sending MIDI."""
    return Action({
        "callback": _NaviIndicatorCallback(color),
        "id": id,
        "useSwitchLeds": True,
        "enableCallback": enable_callback,
    })


def _navi_memory_change(delta, text, color, display, id, enable_callback):
    return Action({
        "callback": _NaviMemoryChangeCallback(delta, text, color),
        "display": display,
        "id": id,
        "useSwitchLeds": True,
        "enableCallback": enable_callback,
    })


class _NaviMemoryChangeCallback(Callback):
    def __init__(self, delta, text, color):
        self._memory = MAPPING_RX_CURRENT_MEMORY()
        self._pc_memory = MAPPING_RX_MEMORY_CHANGE()
        self._memory_select = MAPPING_TX_MEMORY_CHANGE()
        self._delta = delta
        self._text = text
        self._color = color
        super().__init__(mappings = [self._memory, self._pc_memory])

    def init(self, appl, listener = None):
        super().init(appl, listener)
        self._appl = appl

    def push(self):
        current = self._memory.value
        if current is not None:
            target = _clamp(current + self._delta, 0, _MAX_MEMORY)
            # Keep locally selected memory in sync until GX-100 feedback arrives.
            self._memory.value = target
            self._pc_memory.value = target
            self._appl.client.set(self._memory_select, target)
            return

        current_pc = self._pc_memory.value
        if current_pc is None:
            return
        target_pc = _clamp(current_pc + self._delta, 0, _MAX_MEMORY)
        self._pc_memory.value = target_pc
        self._appl.client.set(self._memory_select, target_pc)

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


def _clamp(value, minimum, maximum):
    if value < minimum:
        return minimum
    if value > maximum:
        return maximum
    return value
