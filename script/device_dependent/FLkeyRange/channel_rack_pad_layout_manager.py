from script.actions import ChannelRackNavigationModeChangedAction
from script.constants import ChannelNavigationMode
from script.device_independent.view import (
    ChannelBankNamesHighlightView,
    ChannelBankView,
    ChannelRackDrumPadsView,
    PresetButtonScreenView,
    PresetButtonView,
)
from util.mapped_pad_led_writer import MappedPadLedWriter


class ChannelRackPadLayoutManager:
    def __init__(
        self,
        action_dispatcher,
        pad_led_writer,
        button_led_writer,
        screen_writer,
        fl,
        product_defs,
        model,
        fl_window_manager,
    ):
        channel_rack_pad_led_writer = MappedPadLedWriter(
            pad_led_writer, product_defs.Constants.NotesForPadLayout.value[product_defs.PadLayout.ChannelRack]
        )
        self.channel_selection_dependent_views = {
            PresetButtonScreenView(action_dispatcher, screen_writer, fl),
            PresetButtonView(action_dispatcher, button_led_writer, fl, product_defs),
        }
        self.channel_selection_independent_view = {
            ChannelRackDrumPadsView(action_dispatcher, channel_rack_pad_led_writer, fl, model),
            ChannelBankView(action_dispatcher, button_led_writer, fl, product_defs, model),
            ChannelBankNamesHighlightView(action_dispatcher, fl, model),
        }
        self.fl = fl
        self.action_dispatcher = action_dispatcher
        self.model = model
        self.fl_window_manager = fl_window_manager

    def show(self):
        self.model.channel_rack.navigation_mode = ChannelNavigationMode.Bank
        self.action_dispatcher.dispatch(ChannelRackNavigationModeChangedAction())
        self.action_dispatcher.subscribe(self)
        if self.fl.is_any_channel_selected():
            for view in self.channel_selection_dependent_views:
                view.show()
        for view in self.channel_selection_independent_view:
            view.show()
        self.fl_window_manager.focus_channel_window()

    def hide(self):
        for view in self.channel_selection_dependent_views:
            view.hide()
        for view in self.channel_selection_independent_view:
            view.hide()
        self.action_dispatcher.unsubscribe(self)

    def handle_ChannelSelectionToggleAction(self, action):
        if action.any_channel_selected:
            for view in self.channel_selection_dependent_views:
                view.show()
        else:
            for view in self.channel_selection_dependent_views:
                view.hide()
