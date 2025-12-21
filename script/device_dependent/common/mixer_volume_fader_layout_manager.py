from script.commands import RequestDisableMixerBankingCommand, RequestEnableMixerBankingCommand
from script.constants import Faders
from script.device_independent.view import MixerSoloMuteToggleView, MixerSoloMuteView, MixerVolumeView


class MixerVolumeFaderLayoutManager:
    def __init__(
        self, action_dispatcher, command_dispatcher, product_defs, fl, model, button_led_writer, fl_window_manager
    ):
        self.fl_window_manager = fl_window_manager
        self.command_dispatcher = command_dispatcher
        control_to_index = {
            Faders.FirstControlIndex.value + control: index
            for index, control in enumerate(range(Faders.NumRegularFaders.value))
        }
        self.views = {
            MixerVolumeView(action_dispatcher, fl, model, control_to_index=control_to_index),
            MixerSoloMuteView(action_dispatcher, model, product_defs, fl, button_led_writer),
            MixerSoloMuteToggleView(action_dispatcher, product_defs, model, button_led_writer),
        }

    def show(self):
        self.command_dispatcher.dispatch(RequestEnableMixerBankingCommand())
        for view in self.views:
            view.show()

    def hide(self):
        for view in self.views:
            view.hide()
        self.command_dispatcher.dispatch(RequestDisableMixerBankingCommand())

    def focus_windows(self):
        self.fl_window_manager.hide_last_focused_plugin_window()
        self.fl_window_manager.focus_mixer_window()
