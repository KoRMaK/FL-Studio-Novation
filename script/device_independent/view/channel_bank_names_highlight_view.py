from script.constants import ChannelNavigationSteps, HighlightDuration, Pads
from script.device_independent.util_view.view import View


class ChannelBankNamesHighlightView(View):
    num_steps_per_page = Pads.Num.value

    def __init__(self, action_dispatcher, fl, model):
        super().__init__(action_dispatcher)
        self.fl = fl
        self.model = model

    def _on_show(self):
        if self.model.show_all_highlights_active:
            self._highlight_and_focus_selected_channel_bank_names()

    def _on_hide(self):
        self.fl.turn_off_channelrack_names_highlight()

    @property
    def highlight_duration_ms(self):
        if self.model.show_all_highlights_active:
            return HighlightDuration.WithoutEnd.value
        return HighlightDuration.Default.value

    def handle_ShowHighlightsAction(self, action):
        self._highlight_and_focus_selected_channel_bank_names()

    def handle_HideHighlightsAction(self, action):
        self.fl.turn_off_channelrack_names_highlight()

    def handle_ChannelBankChangeAttemptedAction(self, action):
        self._highlight_and_focus_selected_channel_bank_names(duration_ms=self.highlight_duration_ms)

    def _highlight_and_focus_selected_channel_bank_names(self, *, duration_ms=HighlightDuration.WithoutEnd.value):
        selected_channel = self.model.channel_rack.active_bank * ChannelNavigationSteps.Bank.value
        self.fl.highlight_and_focus_channelrack_names(
            first_channel=selected_channel, num_channels=Pads.Num.value, duration_ms=duration_ms
        )
