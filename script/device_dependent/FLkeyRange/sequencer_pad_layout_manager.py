from script.actions import ChannelRackNavigationModeChangedAction
from script.constants import ChannelNavigationMode, SequencerStepEditState
from script.device_independent.view import (
    ChannelSelectStepsHighlightView,
    ChannelSelectView,
    ExitStepEditLatchModeView,
    PresetButtonScreenView,
    PresetButtonView,
    SequencerPageView,
    SequencerViewManager,
)
from util.mapped_pad_led_writer import MappedPadLedWriter


class SequencerPadLayoutManager:
    def __init__(
        self,
        action_dispatcher,
        command_dispatcher,
        pad_led_writer,
        button_led_writer,
        screen_writer,
        fl,
        product_defs,
        model,
        device_manager,
        fl_window_manager,
    ):
        sequencer_pad_led_writer = MappedPadLedWriter(
            pad_led_writer, product_defs.Constants.NotesForPadLayout.value[product_defs.PadLayout.Sequencer]
        )
        self.channel_selection_dependent_views = {
            ChannelSelectStepsHighlightView(action_dispatcher, fl, model),
            SequencerViewManager(
                action_dispatcher, command_dispatcher, sequencer_pad_led_writer, fl, product_defs, model
            ),
            SequencerPageView(action_dispatcher, button_led_writer, fl, product_defs, model),
            PresetButtonScreenView(action_dispatcher, screen_writer, fl),
            PresetButtonView(action_dispatcher, button_led_writer, fl, product_defs),
        }
        self.channel_select_view = ChannelSelectView(action_dispatcher, button_led_writer, fl, product_defs)
        self.exit_step_edit_latch_mode_view = ExitStepEditLatchModeView(
            action_dispatcher, command_dispatcher, button_led_writer, product_defs
        )
        self.channel_select_button_view = self.channel_select_view

        self.action_dispatcher = action_dispatcher
        self.button_led_writer = button_led_writer
        self.fl = fl
        self.device_manager = device_manager
        self.product_defs = product_defs
        self.model = model
        self.fl_window_manager = fl_window_manager

    def show(self):
        self.model.channel_rack.navigation_mode = ChannelNavigationMode.Single
        self.action_dispatcher.dispatch(ChannelRackNavigationModeChangedAction())
        self.action_dispatcher.subscribe(self)

        if self.fl.is_any_channel_selected():
            for view in self.channel_selection_dependent_views:
                view.show()
        self.channel_select_button_view.show()

        self.fl_window_manager.focus_channel_window()

    def hide(self):
        self.action_dispatcher.unsubscribe(self)

        if self.fl.is_any_channel_selected():
            for view in self.channel_selection_dependent_views:
                view.hide()
        self.channel_select_button_view.hide()

    def handle_ChannelSelectionToggleAction(self, action):
        if action.any_channel_selected:
            for view in self.channel_selection_dependent_views:
                view.show()
        else:
            for view in self.channel_selection_dependent_views:
                view.hide()

    def handle_SequencerStepEditStateChangedAction(self, action):
        if self.model.sequencer.step_edit_state == SequencerStepEditState.EditWaiting:
            self.device_manager.select_pot_layout(self.product_defs.PotLayout.Momentary.value)
        elif self.model.sequencer.step_edit_state == SequencerStepEditState.EditIdle:
            self.device_manager.return_to_previous_pot_layout()

        if self.model.sequencer.step_edit_state == SequencerStepEditState.EditLatch:
            self.channel_select_button_view.hide()
            self.channel_select_button_view = self.exit_step_edit_latch_mode_view
            self.channel_select_button_view.show()
        elif self.channel_select_button_view is self.exit_step_edit_latch_mode_view:
            self.channel_select_button_view.hide()
            self.channel_select_button_view = self.channel_select_view
            self.channel_select_button_view.show()
