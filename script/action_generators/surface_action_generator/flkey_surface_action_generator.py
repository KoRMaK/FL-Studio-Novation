from script.action_generators.surface_action_generator.keyboard_controller_common import (
    KeyboardControllerCommonButtonActionGenerator,
    KeyboardControllerCommonFaderActionGenerator,
    KeyboardControllerCommonFaderLayoutActionGenerator,
    KeyboardControllerCommonPadActionGenerator,
    KeyboardControllerCommonPadLayoutActionGenerator,
    KeyboardControllerCommonPotActionGenerator,
    KeyboardControllerCommonPotLayoutActionGenerator,
    KeyboardControllerCommonScaleActionGenerator,
)


class FLkeySurfaceActionGenerator:
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
            KeyboardControllerCommonFaderLayoutActionGenerator(product_defs),
            KeyboardControllerCommonPadActionGenerator(product_defs),
            KeyboardControllerCommonFaderActionGenerator(product_defs),
        ]

        self.event_to_button = {
            self.product_defs.SurfaceEvent.ButtonMixerRight.value: self.product_defs.Button.MixerRight,
            self.product_defs.SurfaceEvent.ButtonMixerLeft.value: self.product_defs.Button.MixerLeft,
            self.product_defs.SurfaceEvent.ButtonChannelRackUp.value: self.product_defs.Button.ChannelRackUp,
            self.product_defs.SurfaceEvent.ButtonChannelRackDown.value: self.product_defs.Button.ChannelRackDown,
            self.product_defs.SurfaceEvent.ButtonPresetUp.value: self.product_defs.Button.PresetUp,
            self.product_defs.SurfaceEvent.ButtonPresetDown.value: self.product_defs.Button.PresetDown,
            self.product_defs.SurfaceEvent.ButtonPageLeft.value: self.product_defs.Button.PageLeft,
            self.product_defs.SurfaceEvent.ButtonPageRight.value: self.product_defs.Button.PageRight,
            self.product_defs.SurfaceEvent.ButtonTransportPlay.value: self.product_defs.Button.TransportPlay,
            self.product_defs.SurfaceEvent.ButtonTransportStop.value: self.product_defs.Button.TransportStop,
            self.product_defs.SurfaceEvent.ButtonTransportRecord.value: self.product_defs.Button.TransportRecord,
            self.product_defs.SurfaceEvent.ButtonScoreLog.value: self.product_defs.Button.ScoreLog,
            self.product_defs.SurfaceEvent.ButtonShift.value: self.product_defs.Button.Shift,
            self.product_defs.SurfaceEvent.ButtonQuantise.value: self.product_defs.Button.Quantise,
            self.product_defs.SurfaceEvent.ButtonMetronome.value: self.product_defs.Button.Metronome,
            self.product_defs.SurfaceEvent.ButtonUndo.value: self.product_defs.Button.Undo,
            self.product_defs.SurfaceEvent.ButtonRedo.value: self.product_defs.Button.Redo,
            self.product_defs.SurfaceEvent.ButtonTapTempo.value: self.product_defs.Button.TapTempo,
            self.product_defs.SurfaceEvent.ButtonSoloMute.value: self.product_defs.Button.SoloMute,
            self.product_defs.SurfaceEvent.ButtonFader_1.value: self.product_defs.Button.Fader_1,
            self.product_defs.SurfaceEvent.ButtonFader_2.value: self.product_defs.Button.Fader_2,
            self.product_defs.SurfaceEvent.ButtonFader_3.value: self.product_defs.Button.Fader_3,
            self.product_defs.SurfaceEvent.ButtonFader_4.value: self.product_defs.Button.Fader_4,
            self.product_defs.SurfaceEvent.ButtonFader_5.value: self.product_defs.Button.Fader_5,
            self.product_defs.SurfaceEvent.ButtonFader_6.value: self.product_defs.Button.Fader_6,
            self.product_defs.SurfaceEvent.ButtonFader_7.value: self.product_defs.Button.Fader_7,
            self.product_defs.SurfaceEvent.ButtonFader_8.value: self.product_defs.Button.Fader_8,
        }

        self.modified_event_to_button = {
            self.product_defs.SurfaceEvent.ButtonPresetUp.value: self.product_defs.Button.PresetUpShift,
            self.product_defs.SurfaceEvent.ButtonPresetDown.value: self.product_defs.Button.PresetDownShift,
            self.product_defs.SurfaceEvent.ButtonMixerLeft.value: self.product_defs.Button.MixerLeftShift,
            self.product_defs.SurfaceEvent.ButtonMixerRight.value: self.product_defs.Button.MixerRightShift,
            self.product_defs.SurfaceEvent.ButtonChannelRackUp.value: self.product_defs.Button.ChannelRackUpShift,
            self.product_defs.SurfaceEvent.ButtonChannelRackDown.value: self.product_defs.Button.ChannelRackDownShift,
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
