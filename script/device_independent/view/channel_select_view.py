from script.actions import ChannelSelectAction, ChannelSelectAttemptedAction
from script.device_independent.util_view import ScrollingArrowButtonView, View
from script.fl_constants import RefreshFlags


class ChannelSelectView(View):
    def __init__(self, action_dispatcher, surface, fl, product_defs):
        super().__init__(action_dispatcher)
        self.fl = fl
        self.surface = surface
        self.arrow_button_view = ScrollingArrowButtonView(
            action_dispatcher,
            surface,
            product_defs,
            decrement_button="SelectPreviousChannel",
            increment_button="SelectNextChannel",
            on_page_changed=self._on_page_changed,
            on_page_change_attempted=self._on_page_change_attempted,
        )
        self.action_dispatcher = action_dispatcher

    def _on_show(self):
        self._handle_channel_selection_changed()
        self.arrow_button_view.show()

    def _on_hide(self):
        self.arrow_button_view.hide()

    def handle_OnRefreshAction(self, action):
        if action.flags & RefreshFlags.ChannelSelection.value or action.flags & RefreshFlags.ChannelGroup.value:
            self._handle_channel_selection_changed()

    def handle_ChannelSelectionToggleAction(self, action):
        self._handle_channel_selection_changed()

    def _handle_channel_selection_changed(self):
        if self.fl.is_any_channel_selected():
            self.arrow_button_view.set_page_range(0, self.fl.channel_count() - 1)
            self.arrow_button_view.set_active_page(self.fl.selected_channel())
        else:
            self.arrow_button_view.set_page_range(-1, 0)
            self.arrow_button_view.set_active_page(-1)

    def _on_page_changed(self):
        self.fl.select_channel_exclusively(self.arrow_button_view.active_page)
        self.action_dispatcher.dispatch(ChannelSelectAction())

    def _on_page_change_attempted(self):
        self.action_dispatcher.dispatch(ChannelSelectAttemptedAction())
