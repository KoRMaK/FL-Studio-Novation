from script.device_independent.util_view.view import View


class ChannelRackVolumeScreenView(View):
    def __init__(self, action_dispatcher, screen_writer, fl):
        super().__init__(action_dispatcher)
        self.screen_writer = screen_writer
        self.fl = fl

    def handle_ChannelVolumeChangedAction(self, action):
        volume = self.fl.get_channel_volume_dB(action.channel)
        volume_str = "-Inf dB" if volume < -200 else f'{format(volume, ".1f")} dB'
        channel_name = self.fl.get_channel_name(action.channel)
        self.screen_writer.display_parameter(action.control, name=channel_name, value=volume_str)
