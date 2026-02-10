from script.action_generators.surface_action_generator.keyboard_controller_common import (
    KeyboardControllerCommonButtonActionGenerator,
    KeyboardControllerCommonFaderActionGenerator,
    KeyboardControllerCommonFaderLayoutActionGenerator,
    KeyboardControllerCommonPadActionGenerator,
    KeyboardControllerCommonPadLayoutActionGenerator,
    KeyboardControllerCommonPotActionGenerator,
    KeyboardControllerCommonPotLayoutActionGenerator,
)
from script.action_generators.surface_action_generator.surface_actions import ButtonPressedAction, ButtonReleasedAction


class LaunchkeySurfaceActionGenerator:
    def __init__(self, product_defs):
        self.product_defs = product_defs
        self.event_type_to_button = {
            self.product_defs.SurfaceEvent.ButtonShift.value: self.product_defs.Button.Shift,
            self.product_defs.SurfaceEvent.ButtonChannelRackUp.value: self.product_defs.Button.ChannelRackUp,
            self.product_defs.SurfaceEvent.ButtonChannelRackDown.value: self.product_defs.Button.ChannelRackDown,
            self.product_defs.SurfaceEvent.ButtonTransportPlay.value: self.product_defs.Button.TransportPlay,
            self.product_defs.SurfaceEvent.ButtonTransportStop.value: self.product_defs.Button.TransportStop,
            self.product_defs.SurfaceEvent.ButtonTransportRecord.value: self.product_defs.Button.TransportRecord,
            self.product_defs.SurfaceEvent.ButtonMetronome.value: self.product_defs.Button.Metronome,
            self.product_defs.SurfaceEvent.ButtonUndo.value: self.product_defs.Button.Undo,
            self.product_defs.SurfaceEvent.ButtonMixerRight.value: self.product_defs.Button.MixerRight,
            self.product_defs.SurfaceEvent.ButtonMixerLeft.value: self.product_defs.Button.MixerLeft,
        }

        self.common_action_generators = [
            KeyboardControllerCommonButtonActionGenerator(
                self._get_button_for_event, modifier_event=product_defs.SurfaceEvent.ButtonShift.value
            ),
            KeyboardControllerCommonPotActionGenerator(self.product_defs),
            KeyboardControllerCommonPotLayoutActionGenerator(self.product_defs),
            KeyboardControllerCommonPadActionGenerator(self.product_defs),
            KeyboardControllerCommonPadLayoutActionGenerator(self.product_defs),
            KeyboardControllerCommonFaderLayoutActionGenerator(self.product_defs),
            KeyboardControllerCommonFaderActionGenerator(self.product_defs),
        ]

    def _get_button_for_event(self, event, modifier_button_is_held):
        if event == self.product_defs.SurfaceEvent.ButtonShift.value:
            return self.product_defs.Button.Shift
        # No shift-modified buttons yet for Launchkey, but can add here if needed
        return self.event_type_to_button.get(event)

    def handle_midi_event(self, fl_event):
        for action_generator in self.common_action_generators:
            if actions := action_generator.handle_midi_event(fl_event):
                return actions
        return []
