from script.actions import (
    ChannelMuteStateChangedAction,
    ChannelSoloMuteModeChangedAction,
    ChannelSoloStateChangedAction,
)
from script.colour_utils import clamp_brightness, scale_colour
from script.colours import Colours
from script.constants import (
    ChannelNavigationMode,
    ChannelNavigationSteps,
    ChannelSoloMuteMode,
    LedLightingType,
    SoloMuteEditState,
)
from script.device_independent.util_view import View
from script.device_independent.view.solo_mute_edit_state_machine import SoloMuteEditStateMachine
from script.fl_constants import RefreshFlags


class ChannelSoloMuteView(View):
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

    channel_offset_for_button = [0, 1, 2, 3, 4, 5, 6, 7]

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
        self.channel_has_been_interacted_with_in_solo_mode = False

    def _on_show(self):
        self.update_leds()

    def _on_hide(self):
        self.turn_off_leds()

    def _on_state_change(self, previous_state):
        solo_mode_was_active = previous_state != SoloMuteEditState.Mute
        mute_mode_is_active = self.state_machine.state == SoloMuteEditState.Mute
        self.model.channel_solo_mute_mode = (
            ChannelSoloMuteMode.Mute if mute_mode_is_active else ChannelSoloMuteMode.Solo
        )
        self.action_dispatcher.dispatch(ChannelSoloMuteModeChangedAction())
        if solo_mode_was_active and mute_mode_is_active:
            if not self.channel_has_been_interacted_with_in_solo_mode:
                self.unsolo_any_soloed_channels()
            self.channel_has_been_interacted_with_in_solo_mode = False

    def handle_ButtonPressedAction(self, action):
        if action.button in self.button_to_channel_index:
            channel_index = self.button_to_channel_index[action.button]
            if self.state_machine.state == SoloMuteEditState.Mute:
                self.toggle_mute(channel_index)
            else:
                self.toggle_solo(channel_index)
            self.state_machine.mute_button_pressed()

        if action.button == self.product_defs.FunctionToButton.get("ToggleSoloMode"):
            self.state_machine.toggle_pressed()
            self.update_leds()

    def handle_ButtonReleasedAction(self, action):
        if action.button == self.product_defs.FunctionToButton.get("ToggleSoloMode"):
            self.state_machine.toggle_released()
            self.update_leds()

    def handle_ChannelBankChangedAction(self, action):
        self.update_leds()

    def handle_ChannelRackNavigationModeChangedAction(self, action):
        self.update_leds()

    def handle_OnRefreshAction(self, action):
        if (
            action.flags & RefreshFlags.PerformanceLayout.value
            or action.flags & RefreshFlags.ChannelGroup.value
            or action.flags & RefreshFlags.LedUpdate.value
        ):
            self.update_leds()

    @property
    def channel_offset_for_bank(self):
        navigation_mode = self.model.channel_rack.navigation_mode
        if navigation_mode == ChannelNavigationMode.Single.value:
            return self.fl.selected_channel()
        return self.model.channel_rack.active_bank * ChannelNavigationSteps.Bank.value

    @property
    def channels_in_bank(self):
        channel_offset_for_bank = self.channel_offset_for_bank
        return [
            channel_offset_for_bank + channel
            for channel in self.channel_offset_for_button
            if channel_offset_for_bank + channel < self.fl.channel_count()
        ]

    @property
    def button_to_channel_index(self):
        return {
            self.product_defs.FunctionToButton.get(function): channel
            for function, channel in zip(self.button_functions, self.channels_in_bank)
        }

    def get_colour_for_channel(self, channel):
        if self.fl.is_channel_mute_enabled(group_channel=channel):
            return Colours.off
        if self.state_machine.state == SoloMuteEditState.Mute:
            return self.bright_channel_colour(self.fl.get_channel_colour(group_channel=channel))
        if self.fl.is_channel_solo_enabled(group_channel=channel):
            return self.bright_channel_colour(self.fl.get_channel_colour(group_channel=channel))
        return self.dim_channel_colour(self.fl.get_channel_colour(group_channel=channel))

    def update_leds(self):
        self.turn_off_leds()
        for button, channel in self.button_to_channel_index.items():
            colour = self.get_colour_for_channel(channel)
            self.button_led_writer.set_button_colour(button, colour, lighting_type=LedLightingType.RGB)

    def turn_off_leds(self):
        for function in self.button_functions:
            button = self.product_defs.FunctionToButton.get(function)
            self.button_led_writer.set_button_colour(button, Colours.off)

    def unsolo_any_soloed_channels(self):
        for channel in range(self.fl.channel_count()):
            if self.fl.is_channel_solo_enabled(group_channel=channel):
                self.fl.toggle_channel_solo(group_channel=channel)
                return

    def toggle_mute(self, channel):
        enabled = not self.fl.is_channel_mute_enabled(group_channel=channel)
        self.fl.toggle_channel_mute(group_channel=channel)
        self.action_dispatcher.dispatch(ChannelMuteStateChangedAction(channel=channel, enabled=enabled))

    def toggle_solo(self, channel):
        self.channel_has_been_interacted_with_in_solo_mode = True
        enabled = not self.fl.is_channel_solo_enabled(group_channel=channel)
        self.fl.toggle_channel_solo(group_channel=channel)
        self.action_dispatcher.dispatch(ChannelSoloStateChangedAction(channel=channel, enabled=enabled))

    def dim_channel_colour(self, base_colour):
        return scale_colour(base_colour, self.dim_colour_scale_factor)

    def bright_channel_colour(self, base_colour):
        return clamp_brightness(base_colour, minimum=self.bright_colour_min_brightness)
