from .keyboard_controller_common import (
    KeyboardControllerCommonButtonActionGenerator,
    KeyboardControllerCommonPadActionGenerator,
    KeyboardControllerCommonPadLayoutActionGenerator,
    KeyboardControllerCommonPotActionGenerator,
    KeyboardControllerCommonPotLayoutActionGenerator,
    KeyboardControllerCommonScaleActionGenerator,
)


class FLkeyMiniSurfaceActionGenerator:
    def __init__(self, product_defs):
        self.product_defs = product_defs
        self.common_action_generators = [
            KeyboardControllerCommonButtonActionGenerator(
                self._get_button_for_event, modifier_event=product_defs.SurfaceEvent.ButtonShift.value
            ),
            KeyboardControllerCommonPotActionGenerator(product_defs),
            KeyboardControllerCommonScaleActionGenerator(product_defs),
            KeyboardControllerCommonPotLayoutActionGenerator(product_defs),
            KeyboardControllerCommonPadLayoutActionGenerator(product_defs),
            KeyboardControllerCommonPadActionGenerator(product_defs),
        ]
        self.event_to_button = {
            self.product_defs.SurfaceEvent.ButtonChannelRackUp.value: self.product_defs.Button.ChannelRackUp,
            self.product_defs.SurfaceEvent.ButtonChannelRackDown.value: self.product_defs.Button.ChannelRackDown,
            self.product_defs.SurfaceEvent.ButtonTapTempo.value: self.product_defs.Button.TapTempo,
            self.product_defs.SurfaceEvent.ButtonTransportPlay.value: self.product_defs.Button.TransportPlay,
            self.product_defs.SurfaceEvent.ButtonTransportRecord.value: self.product_defs.Button.TransportRecord,
        }
        self.modified_event_to_button = {
            self.product_defs.SurfaceEvent.ButtonMixerRight.value: self.product_defs.Button.MixerRightShift,
            self.product_defs.SurfaceEvent.ButtonMixerLeft.value: self.product_defs.Button.MixerLeftShift,
            self.product_defs.SurfaceEvent.ButtonChannelRackUp.value: self.product_defs.Button.ChannelRackUpShift,
            self.product_defs.SurfaceEvent.ButtonChannelRackDown.value: self.product_defs.Button.ChannelRackDownShift,
            self.product_defs.SurfaceEvent.ButtonPresetUp.value: self.product_defs.Button.PresetUpShift,
            self.product_defs.SurfaceEvent.ButtonPresetDown.value: self.product_defs.Button.PresetDownShift,
        }

    def handle_midi_event(self, fl_event):
        for action_generator in self.common_action_generators:
            if actions := action_generator.handle_midi_event(fl_event):
                return actions
        return []

    def _get_button_for_event(self, event, modifier_button_is_held):
        if event == self.product_defs.SurfaceEvent.ButtonShift.value:
            return self.product_defs.Button.Shift
        if modifier_button_is_held:
            return self.modified_event_to_button.get(event)
        return self.event_to_button.get(event)
