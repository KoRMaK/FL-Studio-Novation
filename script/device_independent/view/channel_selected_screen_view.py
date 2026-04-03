from script.device_independent.util_view.view import View


class ChannelSelectedScreenView(View):
    def __init__(self, action_dispatcher, screen_writer, fl, channel_selection_manager=None):
        super().__init__(action_dispatcher)
        self.screen_writer = screen_writer
        self.fl = fl
        self.channel_selection_manager = channel_selection_manager

    def handle_ChannelSelectAction(self, action):
        if self.channel_selection_manager:
            index = self.channel_selection_manager.get_active_channel()
        else:
            index = self.fl.selected_channel()
        name = self.fl.get_channel_name(index)
        self.screen_writer.display_notification(primary_text="Channel", secondary_text=f"{index + 1} - {name}")
