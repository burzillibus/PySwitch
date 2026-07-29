"""Small local mode selector used by multi-page input profiles."""

from ....controller.actions import Action


class ModeSelector:
    def __init__(self, initial_mode, display = None):
        self.current_mode = initial_mode
        self._display = display
        self._appl = None

    def enabled(self, action):
        return action.id == self.current_mode

    # Action enable callbacks are initialized by the framework before use.
    def init(self, appl):
        self.attach(appl)

    def attach(self, appl):
        self._appl = appl
        self._show_mode()

    def select(self, mode):
        if mode == self.current_mode:
            return

        self.current_mode = mode
        self._show_mode()

        # Refresh each action without resetting its local state. This is
        # important for stomp switches whose LED state is managed locally.
        if not self._appl:
            return
        for input_controller in self._appl.inputs:
            for action in input_controller.actions:
                action.update()

    def _show_mode(self):
        if self._display:
            self._display.text = self.current_mode.upper()


def SELECT_MODE(selector, mode):
    return _SelectModeAction(selector, mode)


class _SelectModeAction(Action):
    def __init__(self, selector, mode):
        super().__init__({"useSwitchLeds": False})
        self._selector = selector
        self._mode = mode

    def init(self, appl, switch):
        super().init(appl, switch)
        self._selector.attach(appl)

    def push(self):
        self._selector.select(self._mode)

    def release(self):
        pass
