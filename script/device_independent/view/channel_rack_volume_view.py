from script.actions import ChannelVolumeChangedAction
from script.constants import ChannelNavigationMode, ChannelNavigationSteps, Pots
from script.device_independent.util_view.view import View
from script.device_independent.view.control_change_rate_limiter import ControlChangeRateLimiter


class ChannelRackVolumeView(View):
    channels_per_bank = Pots.Num.value

    def __init__(self, action_dispatcher, fl, model, *, control_to_index):
        super().__init__(action_dispatcher)
        self.fl = fl
        self.model = model
        self.control_to_index = control_to_index
        self.reset_pickup_on_first_movement = False
        self.control_change_rate_limiter = ControlChangeRateLimiter(action_dispatcher)

    def _on_show(self):
        self.reset_pickup_on_first_movement = True
        self.control_change_rate_limiter.start()

    def _on_hide(self):
        self.control_change_rate_limiter.stop()

    def handle_ChannelBankChangedAction(self, action):
        self.control_change_rate_limiter.reset()
        self.reset_pickup_on_first_movement = True

    def handle_ChannelSelectAction(self, action):
        self.control_change_rate_limiter.reset()
        if self.model.channel_rack.navigation_mode == ChannelNavigationMode.Single.value:
            self._reset_pickup_for_current_channel_bank()

    def handle_ControlChangedAction(self, action):
        index = self.control_to_index.get(action.control)
        if index is None:
            return

        navigation_mode = self.model.channel_rack.navigation_mode
        if navigation_mode is None:
            return

        if navigation_mode == ChannelNavigationMode.Bank.value:
            channel_offset = self.model.channel_rack.active_bank * ChannelNavigationSteps.Bank.value
        elif navigation_mode == ChannelNavigationMode.Single.value:
            channel_offset = self.fl.selected_channel()

        channel = channel_offset + index
        if channel >= self.fl.channel_count():
            return

        if self.reset_pickup_on_first_movement:
            self.reset_pickup_on_first_movement = False
            self._reset_pickup_for_current_channel_bank()

        volume = action.position
        if self.control_change_rate_limiter.forward_control_change_event(channel, volume):
            self.fl.set_channel_volume(channel, volume)
            self.action_dispatcher.dispatch(ChannelVolumeChangedAction(channel=channel, control=action.control))

    def _reset_pickup_for_current_channel_bank(self):
        start_channel = self.model.channel_rack.active_bank * self.channels_per_bank
        for channel in range(start_channel, start_channel + self.channels_per_bank):
            if channel >= self.fl.channel_count():
                break
            self.fl.reset_channel_volume_pickup(channel)
