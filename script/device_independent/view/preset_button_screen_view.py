from script.device_independent.util_view.view import View
from script.fl_constants import RefreshFlags


class PresetButtonScreenView(View):
    def __init__(self, action_dispatcher, screen_writer, fl):
        super().__init__(action_dispatcher)
        self.screen_writer = screen_writer
        self.fl = fl
        self.waiting_for_name_refresh = False

    def handle_PresetChangedAction(self, action):
        # When a preset is changed, it takes a while for it to load.
        # So we need to wait for the right refresh flags before we
        # can request the current preset name.
        self.waiting_for_name_refresh = True

    def handle_OnRefreshAction(self, action):
        if action.flags & RefreshFlags.PluginNames.value and self.waiting_for_name_refresh:
            preset_name = self.fl.get_preset_name()
            self.screen_writer.display_notification(primary_text="Preset", secondary_text=preset_name)
            self.waiting_for_name_refresh = False
