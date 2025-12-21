from script.constants import ChannelNavigationMode, ChannelNavigationSteps, HighlightDuration, Pots
from script.device_independent.util_view.view import View


class ChannelBankControlsHighlightView(View):
    def __init__(self, action_dispatcher, fl, model):
        super().__init__(action_dispatcher)
        self.fl = fl
        self.model = model

    def _on_show(self):
        if self.model.show_all_highlights_active:
            self._highlight_and_focus_selected_channel_bank_controls()

    def _on_hide(self):
        self.fl.turn_off_channelrack_controls_highlight()

    @property
    def highlight_duration_ms(self):
        if self.model.show_all_highlights_active:
            return HighlightDuration.WithoutEnd.value
        return HighlightDuration.Default.value

    def handle_ShowHighlightsAction(self, action):
        self._highlight_and_focus_selected_channel_bank_controls()

    def handle_HideHighlightsAction(self, action):
        self.fl.turn_off_channelrack_controls_highlight()

    def handle_ChannelBankChangeAttemptedAction(self, action):
        if self.model.channel_rack.navigation_mode == ChannelNavigationMode.Bank.value:
            self._highlight_and_focus_selected_channel_bank_controls(duration_ms=self.highlight_duration_ms)

    def handle_ChannelRackNavigationModeChangedAction(self, action):
        self._highlight_and_focus_selected_channel_bank_controls(duration_ms=self.highlight_duration_ms)

    def handle_ChannelSelectAttemptedAction(self, action):
        if self.model.channel_rack.navigation_mode == ChannelNavigationMode.Single.value:
            self._highlight_and_focus_selected_channel_bank_controls(duration_ms=self.highlight_duration_ms)

    def handle_FlGuiChannelSelectAction(self, action):
        self._highlight_selected_channel_bank_controls(duration_ms=self.highlight_duration_ms)

    def _get_first_channel_to_highlight(self):
        navigation_mode = self.model.channel_rack.navigation_mode

        if navigation_mode == ChannelNavigationMode.Bank.value:
            return self.model.channel_rack.active_bank * ChannelNavigationSteps.Bank.value
        if navigation_mode == ChannelNavigationMode.Single.value:
            return self.fl.selected_channel()

        return None

    def _highlight_and_focus_selected_channel_bank_controls(self, *, duration_ms=HighlightDuration.WithoutEnd.value):
        first_channel_to_highlight = self._get_first_channel_to_highlight()

        if first_channel_to_highlight is None:
            self.fl.turn_off_channelrack_controls_highlight()
            return

        self.fl.highlight_and_focus_channelrack_controls(
            first_channel=self._get_first_channel_to_highlight(),
            num_channels=Pots.Num.value,
            duration_ms=duration_ms,
        )

    def _highlight_selected_channel_bank_controls(self, *, duration_ms=HighlightDuration.WithoutEnd.value):
        first_channel_to_highlight = self._get_first_channel_to_highlight()

        if first_channel_to_highlight is None:
            self.fl.turn_off_channelrack_controls_highlight()
            return

        self.fl.highlight_channelrack_controls(
            first_channel=self._get_first_channel_to_highlight(),
            num_channels=Pots.Num.value,
            duration_ms=duration_ms,
        )
