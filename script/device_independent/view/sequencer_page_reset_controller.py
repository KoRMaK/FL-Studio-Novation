from script.actions import SequencerPageResetAction
from script.constants import ChannelNavigationMode, ChannelNavigationSteps
from script.device_independent.util_view import View


class SequencerPageResetController(View):
    def __init__(self, action_dispatcher, model, fl):
        super().__init__(action_dispatcher)
        self.action_dispatcher = action_dispatcher
        self.model = model
        self.fl = fl

    def handle_PatternSelectedAction(self, action):
        self._reset_channelrack_steps_page()

    def _reset_channelrack_steps_page(self):
        self.model.sequencer_active_page = 0
        self.fl.focus_channelrack_steps(first_channel=self._selected_channel, num_channels=1, first_step=0, num_steps=0)
        self.action_dispatcher.dispatch(SequencerPageResetAction())

    @property
    def _selected_channel(self):
        navigation_mode = self.model.channel_rack.navigation_mode
        selected_channel = self.fl.selected_channel()
        if selected_channel is None:
            return 0
        if navigation_mode == ChannelNavigationMode.Bank.value:
            return self.model.channel_rack.active_bank * ChannelNavigationSteps.Bank.value
        if navigation_mode == ChannelNavigationMode.Single.value:
            return selected_channel
        return 0
