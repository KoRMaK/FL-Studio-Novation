from script.constants import Faders
from script.device_independent.view import (
    ChannelBankControlsHighlightView,
    ChannelRackVolumeScreenView,
    ChannelRackVolumeView,
    ChannelSoloMuteScreenView,
    ChannelSoloMuteToggleView,
    ChannelSoloMuteView,
)


class ChannelVolumeFaderLayoutManager:
    def __init__(self, action_dispatcher, fl, product_defs, model, screen_writer, button_led_writer, fl_window_manager):
        self.fl_window_manager = fl_window_manager
        control_to_index = {
            Faders.FirstControlIndex.value + control: index
            for index, control in enumerate(range(Faders.NumRegularFaders.value))
        }
        self.views = {
            ChannelBankControlsHighlightView(action_dispatcher, fl, model),
            ChannelRackVolumeView(action_dispatcher, fl, model, control_to_index=control_to_index),
            ChannelRackVolumeScreenView(action_dispatcher, screen_writer, fl),
            ChannelSoloMuteScreenView(action_dispatcher, fl, screen_writer),
            ChannelSoloMuteView(action_dispatcher, model, product_defs, fl, button_led_writer),
            ChannelSoloMuteToggleView(action_dispatcher, product_defs, model, button_led_writer),
        }

    def show(self):
        for view in self.views:
            view.show()

    def hide(self):
        for view in self.views:
            view.hide()

    def focus_windows(self):
        self.fl_window_manager.hide_last_focused_plugin_window()
        self.fl_window_manager.focus_channel_window()
