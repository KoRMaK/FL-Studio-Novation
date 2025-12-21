from script.device_independent.util_view.view import View


class ChannelSoloMuteScreenView(View):
    def __init__(self, action_dispatcher, fl, screen_writer):
        super().__init__(action_dispatcher)
        self.screen_writer = screen_writer
        self.fl = fl

    def handle_ChannelSoloStateChangedAction(self, action):
        channel_name = self.fl.get_channel_name(action.channel)
        self.screen_writer.display_notification(
            primary_text=channel_name, secondary_text=f"Solo {'On' if action.enabled else 'Off'}"
        )

    def handle_ChannelMuteStateChangedAction(self, action):
        channel_name = self.fl.get_channel_name(action.channel)
        channel_is_muted = action.enabled
        self.screen_writer.display_notification(
            primary_text=channel_name, secondary_text="Muted" if channel_is_muted else "Active"
        )
