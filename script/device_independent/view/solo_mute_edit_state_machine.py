from script.constants import SoloMuteEditState
from util.enum import Enum


class SoloMuteEditStateMachine:
    def __init__(self, *, on_state_change):
        self.state = SoloMuteEditState.Mute
        self.on_state_change = on_state_change

    class Events(Enum):
        TogglePressed = 0
        ToggleReleased = 1
        MuteButtonPressed = 2

    def toggle_pressed(self):
        self._process_event(self.Events.TogglePressed)

    def toggle_released(self):
        self._process_event(self.Events.ToggleReleased)

    def mute_button_pressed(self):
        self._process_event(self.Events.MuteButtonPressed)

    def _process_event(self, event):
        previous_state = self.state
        self.state = self._next(self.state, event)
        if previous_state != self.state:
            self.on_state_change(previous_state)

    def _next(cls, state, event):
        if state == SoloMuteEditState.Mute:
            if event == cls.Events.TogglePressed:
                return SoloMuteEditState.Suspended

        if state == SoloMuteEditState.Suspended:
            if event == cls.Events.ToggleReleased:
                return SoloMuteEditState.SingleTrackSolo
            if event == cls.Events.MuteButtonPressed:
                return SoloMuteEditState.SingleTrackSoloMomentary

        if state == SoloMuteEditState.SingleTrackSolo:
            if event == cls.Events.TogglePressed:
                return SoloMuteEditState.Mute
            if event == cls.Events.MuteButtonPressed:
                return SoloMuteEditState.Mute

        if state == SoloMuteEditState.SingleTrackSoloMomentary:
            if event == cls.Events.ToggleReleased:
                return SoloMuteEditState.Mute

        return state
