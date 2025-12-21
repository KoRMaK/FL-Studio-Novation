import math

from script.actions import PatternSelectBankChangeAttemptedAction, PatternSelectBankChangedAction
from script.constants import PatternSelectBank, ScrollingSpeed
from script.device_independent.util_view import ScrollingArrowButtonView, View
from script.fl_constants import PatternGroups, RefreshFlags


class PatternSelectBankView(View):
    def __init__(self, action_dispatcher, button_led_writer, fl, product_defs, model):
        super().__init__(action_dispatcher)
        self.fl = fl
        self.model = model
        self.arrow_button_view = ScrollingArrowButtonView(
            action_dispatcher,
            button_led_writer,
            product_defs,
            decrement_button="PreviousPatternBank",
            increment_button="NextPatternBank",
            on_page_changed=self._on_page_changed,
            on_page_change_attempted=self._on_page_change_attempted,
            speed=ScrollingSpeed.Slow.value,
        )

    @property
    def _num_pages(self):
        if self.fl.get_active_pattern_group() == PatternGroups.AllPatterns.value:
            number_of_patterns = self.fl.get_number_of_occupied_patterns()
        else:
            number_of_patterns = self.fl.get_number_of_patterns_in_active_group()

        return math.ceil(number_of_patterns / PatternSelectBank.StepsPerBankingIncrement.value)

    def _on_show(self):
        self.arrow_button_view.set_page_range(0, self._num_pages - 1)
        self.arrow_button_view.set_active_page(self.model.pattern_select_active_bank)
        self.arrow_button_view.show()
        if self.arrow_button_view.active_page != self.model.pattern_select_active_bank:
            self._on_page_changed()

    def handle_OnRefreshAction(self, action):
        if action.flags & RefreshFlags.Pattern.value:
            self.arrow_button_view.set_page_range(0, self._num_pages - 1, notify_on_page_change=True)

    def _on_hide(self):
        self.arrow_button_view.hide()

    def _on_page_changed(self):
        self.model.pattern_select_active_bank = self.arrow_button_view.active_page
        self.action_dispatcher.dispatch(PatternSelectBankChangedAction())

    def _on_page_change_attempted(self):
        self.action_dispatcher.dispatch(PatternSelectBankChangeAttemptedAction())
