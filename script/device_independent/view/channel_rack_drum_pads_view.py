from script.actions import ChannelSelectAction
from script.colours import Colours
from script.constants import ChannelNavigationSteps, Notes, Pads
from script.device_independent.util_view.view import View
from script.fl_constants import RefreshFlags


class ChannelRackDrumPadsView(View):
    channel_offset_for_pad = [8, 9, 10, 11, 12, 13, 14, 15, 0, 1, 2, 3, 4, 5, 6, 7]

    def __init__(self, action_dispatcher, pad_led_writer, fl, model):
        super().__init__(action_dispatcher)
        self.fl = fl
        self.model = model
        self.pad_led_writer = pad_led_writer

        self.global_channel_for_held_pad = {}
        self.previously_selected_channel = fl.selected_channel()

        self.group_channel_for_pad = None
        self.pad_for_group_channel = None

    def _on_show(self):
        self._handle_bank_changed()

    def _on_hide(self):
        self._turn_off_leds()

    def handle_PadPressAction(self, action):
        group_channel = self.group_channel_for_pad[action.pad]

        if group_channel >= self.fl.channel_count():
            return

        global_channel = self.fl.get_global_channel(group_channel)

        self.fl.send_note_on(Notes.Default.value, action.velocity, global_channel=global_channel)

        if not self.global_channel_for_held_pad and global_channel != self.fl.get_selected_global_channel():
            # Only select a channel if no other pad is held
            self.fl.select_channel_exclusively(group_channel)
            self.action_dispatcher.dispatch(ChannelSelectAction())

        self.global_channel_for_held_pad[action.pad] = global_channel
        self._update_pad_led(action.pad)

    def handle_PadReleaseAction(self, action):
        global_channel = self.global_channel_for_held_pad.pop(action.pad, None)

        if global_channel is not None:
            self.fl.send_note_off(Notes.Default.value, global_channel=global_channel)
            self._update_pad_led(action.pad)

    def handle_ChannelBankChangedAction(self, action):
        self._handle_bank_changed()

    def handle_OnRefreshAction(self, action):
        if (
            action.flags & RefreshFlags.ChannelSelection.value
            or action.flags & RefreshFlags.LedUpdate.value
            and not self.fl.is_any_channel_selected()
        ):
            self._handle_channel_selection_changed()
        if action.flags & RefreshFlags.PerformanceLayout.value:
            for pad in range(Pads.Num.value):
                self._update_pad_led(pad)
        if action.flags & RefreshFlags.ChannelGroup.value:
            self._handle_group_changed()

    def _handle_bank_changed(self):
        channel_offset_for_bank = self.model.channel_rack.active_bank * ChannelNavigationSteps.Bank.value

        self.group_channel_for_pad = [channel_offset_for_bank + channel for channel in self.channel_offset_for_pad]
        self.pad_for_group_channel = {channel: pad for pad, channel in enumerate(self.group_channel_for_pad)}

        for pad in range(Pads.Num.value):
            self._update_pad_led(pad)

    def _update_pad_led(self, pad):
        group_channel = self.group_channel_for_pad[pad]

        if pad in self.global_channel_for_held_pad:
            self.pad_led_writer.set_pad_colour(pad, Colours.channel_rack_pad_pressed)
        elif group_channel >= self.fl.channel_count():
            self.pad_led_writer.set_pad_colour(pad, Colours.off)
        elif group_channel == self.fl.selected_channel() and self.fl.is_any_channel_selected():
            self.pad_led_writer.set_pad_colour(pad, Colours.channel_rack_pad_selected)
        else:
            channel_colour = self.fl.get_channel_colour(group_channel=group_channel)
            self.pad_led_writer.set_pad_colour(pad, channel_colour)

    def _turn_off_leds(self):
        for pad in range(Pads.Num.value):
            self.pad_led_writer.set_pad_colour(pad, Colours.off)

    def _handle_channel_selection_changed(self):
        previously_selected_channel_pad = self.pad_for_group_channel.get(self.previously_selected_channel)
        currently_selected_channel_pad = self.pad_for_group_channel.get(self.fl.selected_channel())

        if previously_selected_channel_pad is not None:
            self._update_pad_led(previously_selected_channel_pad)
        if currently_selected_channel_pad is not None:
            self._update_pad_led(currently_selected_channel_pad)

        self.previously_selected_channel = self.fl.selected_channel()

    def _handle_group_changed(self):
        self.global_channel_for_held_pad = {}
        self.previously_selected_channel = self.fl.selected_channel()
        self._handle_bank_changed()
