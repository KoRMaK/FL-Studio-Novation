from script.constants import HighlightDuration, Pots
from script.device_independent.util_view.view import View


class MixerBankHighlightView(View):
    tracks_per_bank = Pots.Num.value

    def __init__(self, action_dispatcher, fl, model):
        super().__init__(action_dispatcher)
        self.fl = fl
        self.model = model

    def _on_show(self):
        if self.model.show_all_highlights_active:
            self._highlight_mixer_bank_channels()

    def _on_hide(self):
        # Note: Specifying zero as duration does not yet hide the mixer highlight. Specifying one ms instead.
        self._highlight_mixer_bank_channels(duration_ms=1)

    @property
    def highlight_duration_ms(self):
        if self.model.show_all_highlights_active:
            return HighlightDuration.WithoutEnd.value
        return HighlightDuration.Default.value

    def handle_ShowHighlightsAction(self, action):
        self._highlight_mixer_bank_channels()

    def handle_HideHighlightsAction(self, action):
        # Note: Specifying zero as duration does not yet hide the mixer highlight. Specifying one ms instead.
        self._highlight_mixer_bank_channels(duration_ms=1)

    def handle_MixerBankChangeAttemptedAction(self, action):
        self._highlight_mixer_bank_channels(duration_ms=self.highlight_duration_ms)

    def _highlight_mixer_bank_channels(self, *, duration_ms=HighlightDuration.WithoutEnd.value):
        if not self.model.mixer_tracks_in_active_bank:
            return

        relative_index_of_first_track_in_dock = self.model.mixer_track_active_bank * self.tracks_per_bank
        num_tracks = len(self.model.mixer_tracks_in_active_bank)

        first_track_index = self.model.mixer_tracks_in_active_bank[0]
        last_track_index = self.model.mixer_tracks_in_active_bank[-1]
        self.fl.highlight_tracks(
            relative_index_of_first_track_in_dock,
            num_tracks,
            first_track_index,
            last_track_index,
            duration_ms=duration_ms,
        )
