from script.commands import RequestDisableMixerBankingCommand, RequestEnableMixerBankingCommand
from script.constants import Pots
from script.device_independent.view import MixerVolumeScreenView, MixerVolumeView


class MixerVolumePotLayoutManager:
    def __init__(self, action_dispatcher, command_dispatcher, fl, screen_writer, model, fl_window_manager):
        self.fl_window_manager = fl_window_manager
        self.command_dispatcher = command_dispatcher

        control_to_index = {
            Pots.FirstControlIndex.value + control: index for index, control in enumerate(range(Pots.Num.value))
        }

        self.views = {
            MixerVolumeView(action_dispatcher, fl, model, control_to_index=control_to_index),
            MixerVolumeScreenView(action_dispatcher, screen_writer, fl),
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
