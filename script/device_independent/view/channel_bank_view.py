from math import ceil

from script.actions import ChannelBankChangeAttemptedAction, ChannelBankChangedAction
from script.constants import ChannelNavigationSteps, ScrollingSpeed
from script.device_independent.util_view.scrolling_arrow_button_view import ScrollingArrowButtonView
from script.device_independent.util_view.view import View
from script.fl_constants import RefreshFlags


class ChannelBankView(View):
    def __init__(self, action_dispatcher, surface, fl, product_defs, model):
        super().__init__(action_dispatcher)
        self.fl = fl
        self.model = model
        self.surface = surface
        self.arrow_button_view = ScrollingArrowButtonView(
            action_dispatcher,
            surface,
            product_defs,
            decrement_button="SelectPreviousChannel",
            increment_button="SelectNextChannel",
            on_page_changed=self._on_bank_changed,
            on_page_change_attempted=self._on_page_change_attempted,
            speed=ScrollingSpeed.Slow.value,
        )
        self.action_dispatcher = action_dispatcher

    def _on_show(self):
        self.arrow_button_view.set_page_range(first_page=0, last_page=self._calculate_number_of_banks() - 1)
        self.arrow_button_view.set_active_page(self.model.channel_rack.active_bank)
        self.arrow_button_view.show()

    def _on_hide(self):
        self.arrow_button_view.hide()

    def handle_OnRefreshAction(self, action):
        if action.flags & RefreshFlags.ChannelGroup.value or (
            action.flags & RefreshFlags.TransportStatus.value
            and action.flags & RefreshFlags.ChannelSelection.value
            and action.flags & RefreshFlags.RemoteLinks.value
        ):
            number_of_banks = self._calculate_number_of_banks()
            self.arrow_button_view.set_page_range(
                first_page=0, last_page=number_of_banks - 1, notify_on_page_change=True
            )

    def _calculate_number_of_banks(self):
        return ceil(self.fl.channel_count() / ChannelNavigationSteps.Bank.value)

    def _on_bank_changed(self):
        self.model.channel_rack.active_bank = self.arrow_button_view.active_page
        self.action_dispatcher.dispatch(ChannelBankChangedAction())

    def _on_page_change_attempted(self):
        self.action_dispatcher.dispatch(ChannelBankChangeAttemptedAction())
