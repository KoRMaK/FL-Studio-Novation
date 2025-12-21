from script.device_independent.util_view.view import View
from script.fl_constants import PluginType


class MixerTrackPluginSelectedScreenView(View):
    def __init__(self, action_dispatcher, screen_writer, fl):
        super().__init__(action_dispatcher)
        self.screen_writer = screen_writer
        self.fl = fl

    def handle_MixerTrackPluginSelectedAction(self, action):
        if self.fl.get_selected_plugin_type() != PluginType.Effect:
            return

        track_index = self.fl.get_selected_mixer_track()
        track_name = self.fl.get_mixer_track_name(track_index)
        plugin = self.fl.get_selected_plugin()
        self.screen_writer.display_notification(primary_text=track_name, secondary_text=plugin)
