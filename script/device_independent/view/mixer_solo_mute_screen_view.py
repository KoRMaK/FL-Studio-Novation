from script.device_independent.util_view.view import View


class MixerSoloMuteScreenView(View):
    def __init__(self, action_dispatcher, fl, screen_writer):
        super().__init__(action_dispatcher)
        self.screen_writer = screen_writer
        self.fl = fl

    def handle_MixerSoloStateChangedAction(self, action):
        track_name = self.fl.get_mixer_track_name(action.track)
        self.screen_writer.display_notification(
            primary_text=track_name, secondary_text=f"Solo {'On' if action.enabled else 'Off'}"
        )

    def handle_MixerMuteStateChangedAction(self, action):
        track_name = self.fl.get_mixer_track_name(action.track)
        track_is_muted = action.enabled
        self.screen_writer.display_notification(
            primary_text=track_name, secondary_text="Muted" if track_is_muted else "Active"
        )
