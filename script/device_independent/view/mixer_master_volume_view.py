from script.actions import MixerTrackVolumeChangedAction
from script.constants import Faders
from script.device_independent.util_view.view import View
from script.fl_constants import FlConstants
from util.deadzone_value_converter import DeadzoneValueConverter


class MixerMasterVolumeView(View):
    control_index_for_master_volume = Faders.FirstControlIndex.value + Faders.MasterFaderIndex.value

    def __init__(self, action_dispatcher, fl):
        super().__init__(action_dispatcher)
        self.fl = fl
        self.deadzone_value_converter = DeadzoneValueConverter(maximum=1.0, centre=0.8, width=0.05)
        self.reset_pickup_on_first_movement = False

    def _on_show(self):
        self.reset_pickup_on_first_movement = True

    def handle_ControlChangedAction(self, action):
        if action.control != self.control_index_for_master_volume:
            return

        if self.reset_pickup_on_first_movement:
            self.reset_pickup_on_first_movement = False
            self._reset_pickup()

        volume = self.deadzone_value_converter(action.position)
        self.fl.set_mixer_track_volume(FlConstants.MasterTrackIndex.value, volume)

        self.action_dispatcher.dispatch(
            MixerTrackVolumeChangedAction(track=FlConstants.MasterTrackIndex.value, control=action.control)
        )

    def _reset_pickup(self):
        self.fl.reset_track_volume_pickup(FlConstants.MasterTrackIndex.value)
