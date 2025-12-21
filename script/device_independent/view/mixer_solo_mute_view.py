from script.actions import MixerMuteStateChangedAction, MixerSoloMuteModeChangedAction, MixerSoloStateChangedAction
from script.colour_utils import clamp_brightness, scale_colour
from script.colours import Colours
from script.constants import LedLightingType, MixerSoloMuteMode, SoloMuteEditState
from script.device_independent.util_view import View
from script.device_independent.view.solo_mute_edit_state_machine import SoloMuteEditStateMachine


class MixerSoloMuteView(View):
    button_functions = [
        "ToggleSoloMute_1",
        "ToggleSoloMute_2",
        "ToggleSoloMute_3",
        "ToggleSoloMute_4",
        "ToggleSoloMute_5",
        "ToggleSoloMute_6",
        "ToggleSoloMute_7",
        "ToggleSoloMute_8",
    ]

    def __init__(self, action_dispatcher, model, product_defs, fl, button_led_writer):
        super().__init__(action_dispatcher)
        self.model = model
        self.product_defs = product_defs
        self.fl = fl
        self.button_led_writer = button_led_writer
        self.state_machine = SoloMuteEditStateMachine(on_state_change=self._on_state_change)
        self.bright_colour_min_brightness = 100
        self.dim_colour_scale_factor = 0.25
        self._on_state_change(self.state_machine.state)
        self.track_has_been_interacted_with_in_solo_mode = False

    def _on_show(self):
        self.update_leds()

    def _on_hide(self):
        self.turn_off_leds()

    def _on_state_change(self, previous_state):
        solo_mode_was_active = previous_state != SoloMuteEditState.Mute
        mute_mode_is_active = self.state_machine.state == SoloMuteEditState.Mute
        self.model.mixer_solo_mute_mode = MixerSoloMuteMode.Mute if mute_mode_is_active else MixerSoloMuteMode.Solo
        self.action_dispatcher.dispatch(MixerSoloMuteModeChangedAction())
        if solo_mode_was_active and mute_mode_is_active:
            if not self.track_has_been_interacted_with_in_solo_mode:
                self.unsolo_any_soloed_tracks()
            self.track_has_been_interacted_with_in_solo_mode = False

    @property
    def button_to_track_index(self):
        tracks_in_bank = self.model.mixer_tracks_in_active_bank
        return {
            self.product_defs.FunctionToButton.get(function): track
            for function, track in zip(self.button_functions, tracks_in_bank)
        }

    def handle_ButtonPressedAction(self, action):
        if action.button in self.button_to_track_index:
            track_index = self.button_to_track_index[action.button]
            if self.state_machine.state == SoloMuteEditState.Mute:
                self.toggle_mute(track_index)
            else:
                self.toggle_solo(track_index)
            self.state_machine.mute_button_pressed()

        if action.button == self.product_defs.FunctionToButton.get("ToggleSoloMode"):
            self.state_machine.toggle_pressed()
            self.update_leds()

    def handle_ButtonReleasedAction(self, action):
        if action.button == self.product_defs.FunctionToButton.get("ToggleSoloMode"):
            self.state_machine.toggle_released()
            self.update_leds()

    def handle_MixerBankChangedAction(self, action):
        self.update_leds()

    def handle_AllMixerTracksChangedAction(self, action):
        self.update_leds()

    def get_colour_for_track(self, track_index):
        if self.fl.is_mixer_track_mute_enabled(track_index):
            return Colours.off
        if self.state_machine.state == SoloMuteEditState.Mute:
            return self.bright_track_colour(self.fl.get_mixer_track_colour(track_index))
        if self.fl.is_mixer_track_solo_enabled(track_index):
            return self.bright_track_colour(self.fl.get_mixer_track_colour(track_index))
        return self.dim_track_colour(self.fl.get_mixer_track_colour(track_index))

    def update_leds(self):
        self.turn_off_leds()
        for button, track_index in self.button_to_track_index.items():
            colour = self.get_colour_for_track(track_index)
            self.button_led_writer.set_button_colour(button, colour, lighting_type=LedLightingType.RGB)

    def turn_off_leds(self):
        for function in self.button_functions:
            button = self.product_defs.FunctionToButton.get(function)
            self.button_led_writer.set_button_colour(button, Colours.off)

    def unsolo_any_soloed_tracks(self):
        for track_index in range(self.fl.mixer_track_count()):
            if self.fl.is_mixer_track_solo_enabled(track_index):
                self.fl.toggle_mixer_track_solo(track_index)
                return

    def toggle_mute(self, track_index):
        enabled = not self.fl.is_mixer_track_mute_enabled(track_index)
        self.fl.toggle_mixer_track_mute(track_index)
        self.action_dispatcher.dispatch(MixerMuteStateChangedAction(track=track_index, enabled=enabled))

    def toggle_solo(self, track_index):
        self.track_has_been_interacted_with_in_solo_mode = True
        enabled = not self.fl.is_mixer_track_solo_enabled(track_index)
        self.fl.toggle_mixer_track_solo(track_index)
        self.action_dispatcher.dispatch(MixerSoloStateChangedAction(track=track_index, enabled=enabled))
        if enabled:
            self.fl.select_mixer_track_exclusively(track_index)

    def dim_track_colour(self, base_colour):
        return scale_colour(base_colour, self.dim_colour_scale_factor)

    def bright_track_colour(self, base_colour):
        return clamp_brightness(base_colour, minimum=self.bright_colour_min_brightness)
