from script.actions import (
    SequencerStepEditGroupChangedAction,
    SequencerStepEditStateChangedAction,
    SequencerStepPressAction,
    SequencerStepReleaseAction,
)
from script.commands import ExitStepEditModeCommand
from script.constants import Pads, SequencerStepEditState
from script.device_independent.view import (
    SequencerPadDisplayView,
    SequencerPlayingStepView,
    SequencerStepEditStateMachine,
    SequencerStepToggleView,
)
from script.device_independent.view.show_graph_editor_view import ShowGraphEditorView
from util.timer import Timer


class SequencerViewManager:
    num_steps_per_page = Pads.Num.value
    timer_events_until_latch = 22
    timer_events_between_displayed_step_edit_parameters = 5

    def __init__(self, action_dispatcher, command_dispatcher, pad_led_writer, fl, product_defs, model):
        self.action_dispatcher = action_dispatcher
        self.command_dispatcher = command_dispatcher
        self.model = model
        self.sequencer_pad_display_view = SequencerPadDisplayView(action_dispatcher, pad_led_writer, fl, model)
        self.sequencer_step_toggle_view = SequencerStepToggleView(
            action_dispatcher, command_dispatcher, fl, product_defs, model, self.sequencer_pad_display_view
        )
        self.views = {
            self.sequencer_pad_display_view,
            self.sequencer_step_toggle_view,
            SequencerPlayingStepView(action_dispatcher, model, self.sequencer_pad_display_view),
            ShowGraphEditorView(action_dispatcher, model, fl),
        }
        self.state_machine = SequencerStepEditStateMachine(self._on_state_change)
        self.model.sequencer.step_edit_state = self.state_machine.state
        self.limit_displayed_parameter_change_rate_timer = Timer(action_dispatcher)
        self.step_edit_latch_timer = Timer(action_dispatcher, on_finished=self._on_step_edit_latch_timer_finished)

    def show(self):
        self.action_dispatcher.subscribe(self)
        self.command_dispatcher.register(self, ExitStepEditModeCommand)
        for view in self.views:
            view.show()

    def hide(self):
        for view in self.views:
            view.hide()
        self.limit_displayed_parameter_change_rate_timer.stop()
        self.step_edit_latch_timer.stop()
        self.command_dispatcher.dispatch(ExitStepEditModeCommand())
        self.command_dispatcher.unregister(self, ExitStepEditModeCommand)
        self.action_dispatcher.unsubscribe(self)

    def _step_for_pad(self, pad):
        return self.model.sequencer_active_page * self.num_steps_per_page + pad

    def handle_PadPressAction(self, action):
        if not self.step_edit_latch_timer.finished():
            self.step_edit_latch_timer.start(self.timer_events_until_latch)

        step = self._step_for_pad(action.pad)
        self.action_dispatcher.dispatch(SequencerStepPressAction(step=step))

    def handle_PadReleaseAction(self, action):
        step = self._step_for_pad(action.pad)
        self.action_dispatcher.dispatch(SequencerStepReleaseAction(step=step))

    def handle_SequencerStepEditParameterChangeAttemptedAction(self, action):
        old_edited = self.model.sequencer.step_edit_group.edited
        old_displayed_step_edit_parameter = self.model.sequencer.step_edit_group.displayed_step_edit_parameter

        self.model.sequencer.step_edit_group.edited = True

        if (
            self.limit_displayed_parameter_change_rate_timer.finished()
            or action.parameter.index <= self.model.sequencer.step_edit_group.displayed_step_edit_parameter
        ):
            self.limit_displayed_parameter_change_rate_timer.start(
                self.timer_events_between_displayed_step_edit_parameters
            )
            self.model.sequencer.step_edit_group.displayed_step_edit_parameter = action.parameter.index

        if (
            old_edited != self.model.sequencer.step_edit_group.edited
            or old_displayed_step_edit_parameter != self.model.sequencer.step_edit_group.displayed_step_edit_parameter
        ):
            self.action_dispatcher.dispatch(SequencerStepEditGroupChangedAction())

    def handle_ExitStepEditModeCommand(self, command):
        self._update_state_machine(exit_step_edit_requested=True)

    def handle_SequencerStepEditGroupChangedAction(self, action):
        self._update_state_machine()
        self.sequencer_pad_display_view.redraw()

    def _on_step_edit_latch_timer_finished(self):
        self._update_state_machine()

    def _update_state_machine(self, *, exit_step_edit_requested=False):
        self.state_machine.process_input(
            num_steps_in_step_edit_group=len(self.model.sequencer.step_edit_group.get_steps()),
            step_edit_group_was_edited=self.model.sequencer.step_edit_group.edited,
            enter_latch_mode_timer_finished=self.step_edit_latch_timer.finished(),
            exit_step_edit_requested=exit_step_edit_requested,
        )

    def _on_state_change(self, state):
        self.model.sequencer.step_edit_state = state
        self.step_edit_latch_timer.stop()

        if state == SequencerStepEditState.EditIdle:
            self.model.sequencer.step_edit_group.remove_all_steps()
            self.action_dispatcher.dispatch(SequencerStepEditGroupChangedAction())
        elif state == SequencerStepEditState.EditWaiting:
            self.step_edit_latch_timer.start(self.timer_events_until_latch)

        self.action_dispatcher.dispatch(SequencerStepEditStateChangedAction())
        self.sequencer_pad_display_view.redraw()
