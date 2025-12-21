from script.fl_constants import RefreshFlags


class FLWindowManager:
    def __init__(self, action_dispatcher, fl):
        self.action_dispatcher = action_dispatcher
        self.fl = fl
        self.last_focused_plugin_channel = None
        action_dispatcher.subscribe(self)

        self.selected_channel = self.fl.selected_channel()
        self.num_channels = self.fl.channel_count()

    def focus_mixer_window(self):
        self.fl.ui.focus_mixer_window()

    def focus_channel_window(self):
        self.fl.ui.focus_channel_window()

    def focus_channel_plugin_window(self):
        self.fl.ui.focus_channel_plugin_window()
        self.last_focused_plugin_channel = self.fl.selected_channel()

    def hide_channel_plugin_window(self):
        self.fl.ui.hide_channel_plugin_window()
        if self.fl.selected_channel() == self.last_focused_plugin_channel:
            self.last_focused_plugin_channel = None

    def hide_last_focused_plugin_window(self):
        if self.last_focused_plugin_channel is not None:
            self.fl.ui.hide_channel_plugin_window(channel=self.last_focused_plugin_channel)
        self.last_focused_plugin_channel = None

    def handle_SequencerPageChangeAttemptedAction(self, action):
        self.focus_channel_window()

    def handle_ChannelSelectAction(self, action):
        selected_channel = self.fl.selected_channel()
        num_channels = self.fl.channel_count()
        if selected_channel == self.selected_channel or num_channels > self.num_channels:
            self.num_channels = num_channels
            return
        self.focus_channel_window()
        self.hide_last_focused_plugin_window()
        self.selected_channel = selected_channel

    def handle_SequencerStepPressAction(self, action):
        self.focus_channel_window()

    def handle_ChannelVolumeChangedAction(self, action):
        self.focus_channel_window()

    def handle_ChannelPanChangedAction(self, action):
        self.focus_channel_window()

    def handle_PluginParameterValueChangedAction(self, action):
        plugin_window_not_of_type_channel_is_focused = (
            self.fl.ui.is_any_plugin_window_focused() and not self.fl.ui.is_any_channel_plugin_window_focused()
        )

        if plugin_window_not_of_type_channel_is_focused:
            return

        plugin_window_of_type_channel_is_focused = self.fl.ui.is_any_channel_plugin_window_focused()
        plugin_window_for_selected_channel_is_already_focused = (
            plugin_window_of_type_channel_is_focused and self.fl.selected_channel() == self.last_focused_plugin_channel
        )

        if plugin_window_for_selected_channel_is_already_focused:
            return

        self.focus_channel_plugin_window()

    def handle_MixerBankChangeAttemptedAction(self, action):
        self.focus_mixer_window()

    def handle_ChannelBankChangeAttemptedAction(self, action):
        self.focus_channel_window()

    def handle_ChannelSelectAttemptedAction(self, action):
        self.focus_channel_window()

    def handle_SequencerStepEditParameterChangedAction(self, action):
        self.focus_channel_window()

    def handle_OnRefreshAction(self, action):
        if action.flags & RefreshFlags.ChannelGroup.value:
            self.last_focused_plugin_channel = None
            self.selected_channel = self.fl.selected_channel()
