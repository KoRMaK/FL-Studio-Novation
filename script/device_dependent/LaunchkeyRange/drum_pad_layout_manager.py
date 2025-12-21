from script.actions import FlGuiChannelSelectAction
from script.device_independent import view
from script.fl_constants import RefreshFlags
from util.mapped_pad_led_writer import MappedPadLedWriter


class DrumPadLayoutManager:
    def __init__(self, action_dispatcher, pad_led_writer, button_led_writer, fl, product_defs, model):
        self.action_dispatcher = action_dispatcher
        self.fl = fl
        self.model = model
        pad_led_writer = MappedPadLedWriter(
            pad_led_writer, product_defs.Constants.NotesForPadLayout.value[product_defs.PadLayout.Drum]
        )
        self.channel_selection_dependent_views = {
            view.ChannelSelectNameHighlightView(self.action_dispatcher, self.fl, model),
            view.Default(self.action_dispatcher, pad_led_writer, self.fl, model),
        }
        self.channel_selection_independent_views = {
            view.ChannelSelectView(self.action_dispatcher, button_led_writer, self.fl, product_defs)
        }

    def show(self):
        self.action_dispatcher.subscribe(self)

        self.model.default_instrument_layout.note_offset_for_pad = {
            pad: self.model.default_instrument_layout.Note(note)
            for pad, note in enumerate([4, 5, 6, 7, 12, 13, 14, 15, 0, 1, 2, 3, 8, 9, 10, 11])
        }

        if self.fl.is_any_channel_selected():
            for global_view in self.channel_selection_dependent_views:
                global_view.show()

        for global_view in self.channel_selection_independent_views:
            global_view.show()

    def hide(self):
        if self.fl.is_any_channel_selected():
            for global_view in self.channel_selection_dependent_views:
                global_view.hide()

        for global_view in self.channel_selection_independent_views:
            global_view.hide()

        self.model.default_instrument_layout.note_offset_for_pad = {}

        self.action_dispatcher.unsubscribe(self)

    def handle_OnRefreshAction(self, action):
        if self.fl.is_any_channel_selected():
            if action.flags & RefreshFlags.ChannelSelection.value or action.flags & RefreshFlags.ChannelGroup.value:
                self.action_dispatcher.dispatch(FlGuiChannelSelectAction())

    def handle_ChannelSelectionToggleAction(self, action):
        if action.any_channel_selected:
            for global_view in self.channel_selection_dependent_views:
                global_view.show()
        else:
            for global_view in self.channel_selection_dependent_views:
                global_view.hide()
