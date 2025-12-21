from script.constants import SequencerStepEditState


class SequencerStepEditStateMachine:
    def __init__(self, on_state_change):
        self.on_state_change = on_state_change
        self.state = SequencerStepEditState.EditIdle

    def process_input(
        self,
        *,
        num_steps_in_step_edit_group=0,
        step_edit_group_was_edited=False,
        enter_latch_mode_timer_finished=False,
        exit_step_edit_requested=False,
    ):
        previous_state = self.state
        self.state = self._next(
            self.state,
            num_steps_in_step_edit_group,
            step_edit_group_was_edited,
            enter_latch_mode_timer_finished,
            exit_step_edit_requested,
        )
        if previous_state != self.state:
            self.on_state_change(self.state)

    @staticmethod
    def _next(
        state,
        num_steps_in_step_edit_group,
        step_edit_group_was_edited,
        enter_latch_mode_timer_finished,
        exit_step_edit_requested,
    ):
        if state == SequencerStepEditState.EditIdle:
            if num_steps_in_step_edit_group:
                return SequencerStepEditState.EditWaiting

        if state == SequencerStepEditState.EditWaiting:
            if exit_step_edit_requested:
                return SequencerStepEditState.EditIdle
            if num_steps_in_step_edit_group == 0:
                return SequencerStepEditState.EditIdle
            if enter_latch_mode_timer_finished:
                return SequencerStepEditState.EditLatch
            if step_edit_group_was_edited:
                return SequencerStepEditState.EditQuick

        if state == SequencerStepEditState.EditQuick:
            if exit_step_edit_requested:
                return SequencerStepEditState.EditIdle
            if num_steps_in_step_edit_group == 0:
                return SequencerStepEditState.EditIdle

        if state == SequencerStepEditState.EditLatch:
            if exit_step_edit_requested:
                return SequencerStepEditState.EditIdle

        return state
