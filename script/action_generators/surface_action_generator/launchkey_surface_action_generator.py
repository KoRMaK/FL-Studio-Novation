from script.action_generators.surface_action_generator.keyboard_controller_common import (
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
            KeyboardControllerCommonPotActionGenerator(self.product_defs),
            KeyboardControllerCommonPotLayoutActionGenerator(self.product_defs),
            KeyboardControllerCommonPadActionGenerator(self.product_defs),
            KeyboardControllerCommonPadLayoutActionGenerator(self.product_defs),
            KeyboardControllerCommonFaderLayoutActionGenerator(self.product_defs),
            KeyboardControllerCommonFaderActionGenerator(self.product_defs),
        ]

    def handle_midi_event(self, fl_event):
        for action_generator in self.common_action_generators:
            if actions := action_generator.handle_midi_event(fl_event):
                return actions

        event_type = fl_event.status, fl_event.data1
        if button := self.event_type_to_button.get(event_type):
            if fl_event.data2 == 0:
                return [ButtonReleasedAction(button=button)]
            return [ButtonPressedAction(button=button)]
        return []
