from script.actions import MixerBankChangeAttemptedAction, MixerBankChangedAction
from script.constants import Pots, ScrollingSpeed
from script.device_independent.util_view import View
from script.device_independent.util_view.scrolling_arrow_button_view import ScrollingArrowButtonView
from script.fl_constants import DockSide


class MixerBankButtonView(View):
    tracks_per_bank = Pots.Num.value
    first_mixer_track_index = 1
    ANALOG_LAB_PLUGIN_NAMES = ["Analog Lab", "Analog Lab V"]

    def __init__(self, action_dispatcher, button_led_writer, fl, product_defs, model):
        super().__init__(action_dispatcher)
        self.fl = fl
        self.model = model
        self.product_defs = product_defs
        self.arrow_button_view = ScrollingArrowButtonView(
            action_dispatcher,
            button_led_writer,
            product_defs,
            decrement_button="MixerBankLeft",
            increment_button="MixerBankRight",
            on_page_changed=self._on_page_changed,
            on_page_change_attempted=self._on_page_change_attempt,
            speed=ScrollingSpeed.Slow.value,
        )

    def _is_analog_lab_selected(self):
        """Check if Analog Lab V is the currently selected plugin"""
        selected_plugin = self.fl.get_selected_plugin()
        if selected_plugin is None:
            return False
        return any(name in selected_plugin for name in self.ANALOG_LAB_PLUGIN_NAMES)

    def _on_show(self):
        self._handle_docked_tracks_changed()
        self.arrow_button_view.set_active_page(self.model.mixer_track_active_bank)
        self._update_mixer_bank_state(self.model.mixer_track_active_bank, self._get_tracks_for_center_dock())
        self.arrow_button_view.show()

    def _on_hide(self):
        self.arrow_button_view.hide()

    def handle_ButtonPressedAction(self, action):
        # Skip mixer banking if Analog Lab V is selected
        if self._is_analog_lab_selected():
            if action.button in [
                self.product_defs.FunctionToButton.get("MixerBankLeft"),
                self.product_defs.FunctionToButton.get("MixerBankRight"),
            ]:
                return
        # Let the arrow button view handle it
        self.arrow_button_view.handle_ButtonPressedAction(action)

    def handle_ButtonReleasedAction(self, action):
        # Skip mixer banking if Analog Lab V is selected
        if self._is_analog_lab_selected():
            if action.button in [
                self.product_defs.FunctionToButton.get("MixerBankLeft"),
                self.product_defs.FunctionToButton.get("MixerBankRight"),
            ]:
                return
        # Let the arrow button view handle it
        self.arrow_button_view.handle_ButtonReleasedAction(action)

    def handle_TimerEventAction(self, action):
        # Skip timer events if Analog Lab is selected (prevents scrolling)
        if self._is_analog_lab_selected():
            return
        # Forward timer events for scrolling behavior
        self.arrow_button_view.handle_TimerEventAction(action)

    def _on_page_changed(self):
        self.model.mixer_track_active_bank = self.arrow_button_view.active_page
        self._update_mixer_bank_state(self.model.mixer_track_active_bank, self._get_tracks_for_center_dock())
        self.action_dispatcher.dispatch(MixerBankChangedAction())

    def _on_page_change_attempt(self):
        self.action_dispatcher.dispatch(MixerBankChangeAttemptedAction())

    def _handle_docked_tracks_changed(self):
        tracks_in_center_dock = self._get_tracks_for_center_dock()
        self._update_num_banks(tracks_in_center_dock)

    def _update_mixer_bank_state(self, bank, tracks_in_center_dock):
        first_index = bank * self.tracks_per_bank
        last_index = first_index + self.tracks_per_bank - 1
        self.model.mixer_tracks_in_active_bank = tracks_in_center_dock[first_index : last_index + 1]

    def _update_num_banks(self, tracks_in_center_dock):
        num_pages = (len(tracks_in_center_dock) + self.tracks_per_bank - 1) // self.tracks_per_bank
        self.arrow_button_view.set_page_range(first_page=0, last_page=num_pages - 1)
        self._on_page_changed()

    def _get_tracks_for_center_dock(self):
        return [
            track
            for track in range(self.model.last_mixer_track_index + 1)
            if self.fl.get_dock_side_for_track(track) is DockSide.Center.value
        ]

    def handle_AllMixerTracksChangedAction(self, action):
        self._handle_docked_tracks_changed()
