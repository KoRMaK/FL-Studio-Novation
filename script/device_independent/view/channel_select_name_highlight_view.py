from script.constants import HighlightDuration, Pads
from script.device_independent.util_view.view import View


class ChannelSelectNameHighlightView(View):
    num_steps_per_page = Pads.Num.value

    def __init__(self, action_dispatcher, fl, model):
        super().__init__(action_dispatcher)
        self.fl = fl
        self.model = model

    def _on_show(self):
        if self.model.show_all_highlights_active:
            self._highlight_and_focus_selected_channel()

    def _on_hide(self):
        self.fl.turn_off_channelrack_names_highlight()

    @property
    def highlight_duration_ms(self):
        if self.model.show_all_highlights_active:
            return HighlightDuration.WithoutEnd.value
        return HighlightDuration.Default.value

    def handle_ShowHighlightsAction(self, action):
        self._highlight_and_focus_selected_channel()

    def handle_HideHighlightsAction(self, action):
        self.fl.turn_off_channelrack_names_highlight()

    def handle_FlGuiChannelSelectAction(self, action):
        self._highlight_selected_channel(duration_ms=self.highlight_duration_ms)

    def handle_ChannelSelectAttemptedAction(self, action):
        self._highlight_and_focus_selected_channel(duration_ms=self.highlight_duration_ms)

    def _highlight_and_focus_selected_channel(self, *, duration_ms=HighlightDuration.WithoutEnd.value):
        if not self.fl.is_any_channel_selected():
            self.fl.turn_off_channelrack_names_highlight()
            return

        self.fl.highlight_and_focus_channelrack_names(
            first_channel=self.fl.selected_channel(), num_channels=1, duration_ms=duration_ms
        )

    def _highlight_selected_channel(self, *, duration_ms=HighlightDuration.WithoutEnd.value):
        if not self.fl.is_any_channel_selected():
            self.fl.turn_off_channelrack_names_highlight()
            return

        self.fl.highlight_channelrack_names(
            first_channel=self.fl.selected_channel(), num_channels=1, duration_ms=duration_ms
        )
