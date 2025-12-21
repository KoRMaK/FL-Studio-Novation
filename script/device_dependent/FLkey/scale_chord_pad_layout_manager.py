from script.actions import ChannelRackNavigationModeChangedAction, FlGuiChannelSelectAction
from script.constants import ChannelNavigationMode
from script.device_independent.view import (
    ChannelSelectNameHighlightView,
    ChannelSelectView,
    PresetButtonScreenView,
    PresetButtonView,
)
from script.fl_constants import RefreshFlags


class ScaleChordPadLayoutManager:
    def __init__(self, action_dispatcher, button_led_writer, screen_writer, fl, product_defs, model):
        self.channel_selection_dependent_views = {
            ChannelSelectNameHighlightView(action_dispatcher, fl, model),
            PresetButtonScreenView(action_dispatcher, screen_writer, fl),
            PresetButtonView(action_dispatcher, button_led_writer, fl, product_defs),
        }
        self.channel_selection_independent_views = {
            ChannelSelectView(action_dispatcher, button_led_writer, fl, product_defs)
        }
        self.fl = fl
        self.action_dispatcher = action_dispatcher
        self.model = model

    def show(self):
        self.model.channel_rack.navigation_mode = ChannelNavigationMode.Single
        self.action_dispatcher.dispatch(ChannelRackNavigationModeChangedAction())
        self.action_dispatcher.subscribe(self)
        if self.fl.is_any_channel_selected():
            for view in self.channel_selection_dependent_views:
                view.show()
        for view in self.channel_selection_independent_views:
            view.show()

    def hide(self):
        for view in self.channel_selection_dependent_views:
            view.hide()
        for view in self.channel_selection_independent_views:
            view.hide()
        self.action_dispatcher.unsubscribe(self)

    def handle_ChannelSelectionToggleAction(self, action):
        if action.any_channel_selected:
            for view in self.channel_selection_dependent_views:
                view.show()
        else:
            for view in self.channel_selection_dependent_views:
                view.hide()

    def handle_OnRefreshAction(self, action):
        if self.fl.is_any_channel_selected():
            if action.flags & RefreshFlags.ChannelSelection.value or action.flags & RefreshFlags.ChannelGroup.value:
                self.action_dispatcher.dispatch(FlGuiChannelSelectAction())
