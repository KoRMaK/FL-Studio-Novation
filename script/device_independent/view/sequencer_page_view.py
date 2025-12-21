from script.actions import FlGuiChannelSelectAction, SequencerPageChangeAttemptedAction, SequencerPageChangedAction
from script.constants import Pads
from script.device_independent.util_view import ArrowButtonView, View
from script.fl_constants import FlConstants, RefreshFlags


class SequencerPageView(View):
    num_steps_per_page = Pads.Num.value

    def __init__(self, action_dispatcher, surface, fl, product_defs, model):
        super().__init__(action_dispatcher)
        num_pages = (FlConstants.MaxStepsPerPattern.value + self.num_steps_per_page - 1) // self.num_steps_per_page
        self.arrow_button_view = ArrowButtonView(
            action_dispatcher,
            surface,
            product_defs,
            increment_button="SequencerStepsPageRight",
            decrement_button="SequencerStepsPageLeft",
            last_page=num_pages - 1,
            on_page_changed=self._on_page_changed,
            on_page_change_attempted=self._on_page_change_attempted,
        )
        self.action_dispatcher = action_dispatcher
        self.fl = fl
        self.model = model

    def _on_show(self):
        self.arrow_button_view.set_active_page(self.model.sequencer_active_page)
        self.arrow_button_view.show()

    def _on_hide(self):
        self.arrow_button_view.hide()

    def _on_page_changed(self):
        self.model.sequencer_active_page = self.arrow_button_view.active_page
        self.action_dispatcher.dispatch(SequencerPageChangedAction())

    def _on_page_change_attempted(self):
        self.action_dispatcher.dispatch(SequencerPageChangeAttemptedAction())

    def handle_SequencerPageResetAction(self, action):
        self.arrow_button_view.set_active_page(0)

    def handle_OnRefreshAction(self, action):
        if action.flags & RefreshFlags.ChannelSelection.value and self.fl.is_any_channel_selected():
            self.action_dispatcher.dispatch(FlGuiChannelSelectAction())
