from script.actions import MixerTrackSelectedAction
from script.constants import ScrollingSpeed
from script.device_independent.util_view import SingleButtonView, View
from script.fl_constants import DockSide, FlConstants
from util.scroller import Scroller


class MixerTrackSelectView(View):
    def __init__(self, action_dispatcher, product_defs, model, button_led_writer, fl):
        super().__init__(action_dispatcher)
        self.product_defs = product_defs
        self.fl = fl
        self.model = model

        self.select_previous_track_button = SingleButtonView(
            button_led_writer, product_defs, "SelectPreviousMixerTrack"
        )
        self.select_next_track_button = SingleButtonView(button_led_writer, product_defs, "SelectNextMixerTrack")
        self.scroller = Scroller(self._on_scroll_step, ScrollingSpeed.Default.value)

    def _on_show(self):
        self.select_previous_track_button.show()
        self.select_next_track_button.show()

    def _on_hide(self):
        self.select_previous_track_button.hide()
        self.select_next_track_button.hide()

    def handle_TimerEventAction(self, action):
        self.scroller.tick()

    def handle_ButtonPressedAction(self, action):
        if action.button == self.select_previous_track_button.button:
            self._handle_select_previous_track_button_pressed()
        elif action.button == self.select_next_track_button.button:
            self._handle_select_next_track_button_pressed()

    def handle_ButtonReleasedAction(self, action):
        if action.button == self.select_previous_track_button.button:
            self._handle_select_previous_track_button_released()
        elif action.button == self.select_next_track_button.button:
            self._handle_select_next_track_button_released()

    def _handle_select_previous_track_button_pressed(self):
        self.scroller.set_active()
        self.select_previous_track_button.set_pressed()
        self._select_previous_mixer_track()

    def _handle_select_next_track_button_pressed(self):
        self.scroller.set_active()
        self.select_next_track_button.set_pressed()
        self._select_next_mixer_track()

    def _handle_select_previous_track_button_released(self):
        self.select_previous_track_button.set_not_pressed()
        if not self.select_next_track_button.is_pressed:
            self.scroller.set_not_active()

    def _handle_select_next_track_button_released(self):
        self.select_next_track_button.set_not_pressed()
        if not self.select_previous_track_button.is_pressed:
            self.scroller.set_not_active()

    def _on_scroll_step(self):
        if self.select_next_track_button.is_pressed:
            self._select_next_mixer_track()
        else:
            self._select_previous_mixer_track()

    def _get_tracks_for_dock_side(self, dock_side):
        return [
            track
            for track in range(self.model.last_mixer_track_index + 1)
            if self.fl.get_dock_side_for_track(track) is dock_side and track != FlConstants.CurrentTrackIndex.value
        ]

    def _get_previous_and_next_mixer_track(self, current_mixer_track_index):
        all_tracks = self._get_all_tracks_in_displayed_order()

        index_in_list = None
        for list_index, track_index in enumerate(all_tracks):
            if track_index == current_mixer_track_index:
                index_in_list = list_index
                break

        if index_in_list is None:
            return FlConstants.MasterTrackIndex.value, FlConstants.MasterTrackIndex.value

        previous_index_in_list = index_in_list - 1
        next_index_in_list = (index_in_list + 1) % len(all_tracks)
        return all_tracks[previous_index_in_list], all_tracks[next_index_in_list]

    def _get_all_tracks_in_displayed_order(self):
        tracks_for_left_dock = self._get_tracks_for_dock_side(DockSide.Left.value)
        tracks_for_center_dock = self._get_tracks_for_dock_side(DockSide.Center.value)
        tracks_for_right_dock = self._get_tracks_for_dock_side(DockSide.Right.value)
        return tracks_for_left_dock + tracks_for_center_dock + tracks_for_right_dock

    def _select_previous_mixer_track(self):
        selected_mixer_track = self.fl.get_selected_mixer_track()

        if selected_mixer_track is None:
            self.fl.select_mixer_track_exclusively(FlConstants.MasterTrackIndex.value)
        else:
            previous_track, _ = self._get_previous_and_next_mixer_track(selected_mixer_track)
            self.fl.select_mixer_track_exclusively(previous_track)

        self.action_dispatcher.dispatch(MixerTrackSelectedAction())

    def _select_next_mixer_track(self):
        selected_mixer_track = self.fl.get_selected_mixer_track()

        if selected_mixer_track is None:
            self.fl.select_mixer_track_exclusively(FlConstants.MasterTrackIndex.value)
        else:
            _, next_track = self._get_previous_and_next_mixer_track(selected_mixer_track)
            self.fl.select_mixer_track_exclusively(next_track)

        self.action_dispatcher.dispatch(MixerTrackSelectedAction())
