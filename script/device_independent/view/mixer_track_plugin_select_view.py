from script.actions import MixerTrackPluginSelectedAction
from script.device_independent.util_view import SingleButtonView, View
from script.fl_constants import FlConstants, PluginType


class MixerTrackPluginSelectView(View):
    def __init__(self, action_dispatcher, button_led_writer, fl, product_defs):
        super().__init__(action_dispatcher)
        self.fl = fl
        self.action_dispatcher = action_dispatcher
        self.product_defs = product_defs
        self.previous_mixer_track_plugin_button = SingleButtonView(
            button_led_writer, product_defs, "SelectPreviousMixerTrackPlugin"
        )
        self.next_mixer_track_plugin_button = SingleButtonView(
            button_led_writer, product_defs, "SelectNextMixerTrackPlugin"
        )

    def _on_show(self):
        self.previous_mixer_track_plugin_button.show()
        self.next_mixer_track_plugin_button.show()

    def _on_hide(self):
        self.previous_mixer_track_plugin_button.hide()
        self.next_mixer_track_plugin_button.hide()

    def handle_ButtonPressedAction(self, action):
        if action.button == self.product_defs.FunctionToButton.get("SelectPreviousMixerTrackPlugin"):
            self._handle_select_previous_mixer_track_plugin_button_pressed()
            self.previous_mixer_track_plugin_button.set_pressed()

        if action.button == self.product_defs.FunctionToButton.get("SelectNextMixerTrackPlugin"):
            self._handle_select_next_mixer_track_plugin_button_pressed()
            self.next_mixer_track_plugin_button.set_pressed()

    def handle_ButtonReleasedAction(self, action):
        if action.button == self.product_defs.FunctionToButton.get("SelectPreviousMixerTrackPlugin"):
            self.previous_mixer_track_plugin_button.set_not_pressed()

        if action.button == self.product_defs.FunctionToButton.get("SelectNextMixerTrackPlugin"):
            self.next_mixer_track_plugin_button.set_not_pressed()

    def _handle_select_previous_mixer_track_plugin_button_pressed(self):
        selected_mixer_track = self.fl.get_selected_mixer_track()

        if selected_mixer_track is None:
            self._select_first_valid_plugin_on_track(FlConstants.MasterTrackIndex.value)
            return

        self._select_previous_valid_plugin_on_selected_track()

    def _handle_select_next_mixer_track_plugin_button_pressed(self):
        selected_mixer_track = self.fl.get_selected_mixer_track()

        if selected_mixer_track is None:
            self._select_first_valid_plugin_on_track(FlConstants.MasterTrackIndex.value)
            return

        self._select_next_valid_plugin_on_selected_track()

    def _get_first_valid_plugin_index_in_range(self, track, indices):
        for index in indices:
            if self.fl.plugin_is_valid(track, index):
                return index
        return None

    def _selected_track_has_a_plugin_selected(self):
        selected_mixer_track = self.fl.get_selected_mixer_track()
        selected_plugin_type = self.fl.get_selected_plugin_type()
        track_index_for_selected_plugin, _ = self.fl.get_selected_plugin_position()
        return selected_plugin_type == PluginType.Effect and track_index_for_selected_plugin == selected_mixer_track

    def _get_selected_plugin_index(self):
        _, selected_plugin_index = self.fl.get_selected_plugin_position()
        return selected_plugin_index

    def _select_first_valid_plugin_on_track(self, track):
        self.fl.select_mixer_track_exclusively(track)
        first_valid_plugin_index = self._get_first_valid_plugin_index_in_range(
            track, range(FlConstants.NumMixerEffectPluginSlots.value)
        )
        if first_valid_plugin_index is not None:
            self._select_mixer_plugin(track, first_valid_plugin_index)

    def _select_next_valid_plugin_on_selected_track(self):
        if not self._selected_track_has_a_plugin_selected():
            self._select_first_valid_plugin_on_track(self.fl.get_selected_mixer_track())
            return

        selected_track_index = self.fl.get_selected_mixer_track()
        selected_plugin_index = self._get_selected_plugin_index()
        next_valid_plugin_index = self._get_first_valid_plugin_index_in_range(
            selected_track_index,
            range(selected_plugin_index + 1, FlConstants.NumMixerEffectPluginSlots.value),
        )
        new_plugin_index = selected_plugin_index if next_valid_plugin_index is None else next_valid_plugin_index
        self._select_mixer_plugin(selected_track_index, new_plugin_index)

    def _select_previous_valid_plugin_on_selected_track(self):
        if not self._selected_track_has_a_plugin_selected():
            self._select_first_valid_plugin_on_track(self.fl.get_selected_mixer_track())
            return

        selected_track_index = self.fl.get_selected_mixer_track()
        selected_plugin_index = self._get_selected_plugin_index()
        next_valid_plugin_index = self._get_first_valid_plugin_index_in_range(
            selected_track_index, reversed(range(selected_plugin_index))
        )
        new_plugin_index = selected_plugin_index if next_valid_plugin_index is None else next_valid_plugin_index
        self._select_mixer_plugin(selected_track_index, new_plugin_index)

    def _select_mixer_plugin(self, track_index, plugin_index):
        self.fl.ui.focus_mixer_plugin_window(track_index, plugin_index)
        self.action_dispatcher.dispatch(MixerTrackPluginSelectedAction())
