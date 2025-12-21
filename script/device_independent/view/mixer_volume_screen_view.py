from script.constants import Faders
from script.device_independent.util_view.view import View
from script.fl_constants import FlConstants
from util.timer import Timer


class MixerVolumeScreenView(View):
    def __init__(self, action_dispatcher, screen_writer, fl):
        super().__init__(action_dispatcher)
        self.screen_writer = screen_writer
        self.fl = fl
        self.master_volume_notification_update_timer = None

    def _on_hide(self):
        self.stop_master_volume_notification_update_timer()

    def handle_MixerTrackVolumeChangedAction(self, action):
        self.stop_master_volume_notification_update_timer()

        if action.track == FlConstants.MasterTrackIndex.value:
            self.handle_master_track_volume_changed()
        else:
            self.handle_regular_track_volume_changed(action.track, action.control)

    def handle_master_track_volume_changed(self):
        self.start_master_volume_notification_update_timer()
        self.display_volume_changed_notification(
            FlConstants.MasterTrackIndex.value, Faders.FirstControlIndex.value + Faders.MasterFaderIndex.value
        )

    def stop_master_volume_notification_update_timer(self):
        if self.master_volume_notification_update_timer is not None:
            self.master_volume_notification_update_timer.stop()
            self.master_volume_notification_update_timer = None

    def start_master_volume_notification_update_timer(self):
        self.master_volume_notification_update_timer = Timer(
            self.action_dispatcher,
            on_finished=lambda: self.display_volume_changed_notification(
                FlConstants.MasterTrackIndex.value, Faders.FirstControlIndex.value + Faders.MasterFaderIndex.value
            ),
        )
        timer_events_until_notification_update = 5
        self.master_volume_notification_update_timer.start(timer_events_until_notification_update)

    def handle_regular_track_volume_changed(self, track, control):
        self.display_volume_changed_notification(track, control)

    def display_volume_changed_notification(self, track, control):
        volume = self.fl.get_mixer_track_volume_dB(track)
        volume_str = "-Inf dB" if volume < -200 else f'{format(volume, ".1f")} dB'
        track_name = self.fl.get_mixer_track_name(track)
        self.screen_writer.display_parameter(control, name=track_name, value=volume_str)
