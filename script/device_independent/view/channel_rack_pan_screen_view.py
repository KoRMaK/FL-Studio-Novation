from script.device_independent.util_view.view import View


class ChannelRackPanScreenView(View):
    def __init__(self, action_dispatcher, screen_writer, fl):
        super().__init__(action_dispatcher)
        self.screen_writer = screen_writer
        self.fl = fl

    def handle_ChannelPanChangedAction(self, action):
        pan = action.value
        if abs(pan) < 1e-6:
            pan_str = "C"
        elif pan < 0:
            pan_str = f'{format(abs(pan) * 100, ".0f")}L'
        else:
            pan_str = f'{format(abs(pan) * 100, ".0f")}R'

        channel_name = self.fl.get_channel_name(action.channel)
        self.screen_writer.display_parameter(action.control, name=channel_name, value=pan_str)
